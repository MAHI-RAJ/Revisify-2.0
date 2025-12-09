import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDocStore } from '@/state/docStore';
import { useAuthStore } from '@/state/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader } from '@/components/Loader';
import { Plus, FileText, Clock, ArrowRight, Trash2, MessageSquare } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

export default function Home() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { documents, fetchDocuments, deleteDocument, isLoading, error } = useDocStore();

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return 'bg-success/10 text-success';
      case 'processing': return 'bg-warning/10 text-warning';
      case 'failed': return 'bg-destructive/10 text-destructive';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.name?.split(' ')[0] || 'there'}!</h1>
          <p className="text-muted-foreground mt-1">Continue where you left off</p>
        </div>
        <Button onClick={() => navigate('/upload')} className="gradient-primary">
          <Plus className="mr-2 h-4 w-4" /> Upload Document
        </Button>
      </div>

      {/* Documents Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12"><Loader size="lg" text="Loading documents..." /></div>
      ) : error ? (
        <Card className="text-center py-12">
          <CardContent>
            <p className="text-destructive">{error}</p>
            <Button onClick={() => fetchDocuments()} variant="outline" className="mt-4">Retry</Button>
          </CardContent>
        </Card>
      ) : documents.length === 0 ? (
        <Card className="text-center py-16">
          <CardContent className="space-y-4">
            <div className="mx-auto h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
              <FileText className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h3 className="text-xl font-semibold">No documents yet</h3>
              <p className="text-muted-foreground mt-1">Upload your first document to get started</p>
            </div>
            <Button onClick={() => navigate('/upload')} className="gradient-primary">
              <Plus className="mr-2 h-4 w-4" /> Upload Document
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {documents.map((doc) => (
            <Card key={doc.id} className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                  <span className={cn('text-xs font-medium px-2 py-1 rounded-full capitalize', getStatusColor(doc.status))}>
                    {doc.status}
                  </span>
                </div>
                <CardTitle className="text-lg mt-3 line-clamp-1">{doc.title}</CardTitle>
                <CardDescription className="flex items-center gap-2 text-xs">
                  <Clock className="h-3 w-3" />
                  {format(new Date(doc.createdAt), 'MMM d, yyyy')}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex gap-2">
                  {doc.status === 'ready' && (
                    <>
                      <Button size="sm" className="flex-1" onClick={() => navigate(`/roadmap/${doc.id}`)}>
                        <ArrowRight className="mr-1 h-3 w-3" /> Learn
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => navigate(`/ask/${doc.id}`)}>
                        <MessageSquare className="h-3 w-3" />
                      </Button>
                    </>
                  )}
                  {doc.status === 'processing' && (
                    <Button size="sm" className="flex-1" onClick={() => navigate(`/processing/${doc.id}`)}>
                      View Progress
                    </Button>
                  )}
                  <Button size="sm" variant="ghost" onClick={() => deleteDocument(doc.id)} className="text-destructive hover:text-destructive">
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
