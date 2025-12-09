import { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { ragApi, ChatMessage, DocumentSection } from '@/api/ragApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Loader, LoaderDots } from '@/components/Loader';
import { toast } from '@/components/Toast';
import { Send, FileText, Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function AskDoc() {
  const { docId } = useParams<{ docId: string }>();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sections, setSections] = useState<DocumentSection[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (docId) {
      setIsLoading(true);
      ragApi.getDocumentSections(docId).then(setSections).catch(() => {}).finally(() => setIsLoading(false));
    }
  }, [docId]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !docId || isSending) return;
    const userMessage: ChatMessage = { id: Date.now().toString(), role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsSending(true);

    try {
      const response = await ragApi.sendMessage(docId, input);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      toast({ type: 'error', title: 'Failed to get response' });
    } finally {
      setIsSending(false);
    }
  };

  if (isLoading) return <div className="flex justify-center py-20"><Loader size="lg" text="Loading..." /></div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="grid lg:grid-cols-4 gap-6 h-[calc(100vh-12rem)]">
        {/* Sidebar */}
        <Card className="lg:col-span-1 hidden lg:block">
          <CardHeader><CardTitle className="text-sm flex items-center gap-2"><FileText className="h-4 w-4" />Document Sections</CardTitle></CardHeader>
          <CardContent>
            <ScrollArea className="h-[calc(100vh-20rem)]">
              <div className="space-y-2">
                {sections.map((s) => (
                  <button key={s.id} className="w-full text-left p-2 rounded-lg hover:bg-muted text-sm transition-colors">
                    <span className="font-medium line-clamp-1">{s.title}</span>
                    <span className="text-xs text-muted-foreground">Pages {s.pageStart}-{s.pageEnd}</span>
                  </button>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Chat */}
        <Card className="lg:col-span-3 flex flex-col">
          <CardHeader className="border-b"><CardTitle className="flex items-center gap-2"><Bot className="h-5 w-5 text-primary" />Ask Your Document</CardTitle></CardHeader>
          <CardContent className="flex-1 flex flex-col p-0">
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Ask any question about your document</p>
                  </div>
                )}
                {messages.map((msg) => (
                  <div key={msg.id} className={cn('flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                    {msg.role === 'assistant' && <div className="h-8 w-8 rounded-full gradient-primary flex items-center justify-center flex-shrink-0"><Bot className="h-4 w-4 text-primary-foreground" /></div>}
                    <div className={cn('max-w-[80%] rounded-2xl px-4 py-2', msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted')}>
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-border/50 space-y-1">
                          {msg.citations.map((c, i) => (<p key={i} className="text-xs opacity-70">📄 {c.text}</p>))}
                        </div>
                      )}
                    </div>
                    {msg.role === 'user' && <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0"><User className="h-4 w-4" /></div>}
                  </div>
                ))}
                {isSending && <div className="flex gap-3"><div className="h-8 w-8 rounded-full gradient-primary flex items-center justify-center"><Bot className="h-4 w-4 text-primary-foreground" /></div><div className="bg-muted rounded-2xl px-4 py-3"><LoaderDots /></div></div>}
                <div ref={scrollRef} />
              </div>
            </ScrollArea>
            <div className="p-4 border-t">
              <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
                <Input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask a question..." disabled={isSending} className="flex-1" />
                <Button type="submit" disabled={!input.trim() || isSending} className="gradient-primary"><Send className="h-4 w-4" /></Button>
              </form>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
