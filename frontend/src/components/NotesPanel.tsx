import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { FileText, Save, Loader2, Check } from 'lucide-react';

interface NotesPanelProps {
  initialContent?: string;
  onSave: (content: string) => Promise<void>;
  autoSaveDelay?: number;
}

export function NotesPanel({ initialContent = '', onSave, autoSaveDelay = 5000 }: NotesPanelProps) {
  const [content, setContent] = useState(initialContent);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setContent(initialContent);
    setHasChanges(false);
  }, [initialContent]);

  // Auto-save effect
  useEffect(() => {
    if (!hasChanges) return;
    
    const timer = setTimeout(async () => {
      await handleSave();
    }, autoSaveDelay);

    return () => clearTimeout(timer);
  }, [content, hasChanges]);

  const handleChange = (value: string) => {
    setContent(value);
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (!hasChanges) return;
    setIsSaving(true);
    try {
      await onSave(content);
      setLastSaved(new Date());
      setHasChanges(false);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2 text-lg">
            <FileText className="h-5 w-5 text-primary" />
            Your Notes
          </span>
          <div className="flex items-center gap-2">
            {lastSaved && (
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Check className="h-3 w-3 text-success" />
                Saved {lastSaved.toLocaleTimeString()}
              </span>
            )}
            {hasChanges && (
              <span className="text-xs text-warning">Unsaved changes</span>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea
          value={content}
          onChange={(e) => handleChange(e.target.value)}
          placeholder="Take notes as you learn... Your notes are automatically saved."
          className="min-h-[250px] resize-none"
        />
        <div className="flex justify-between items-center">
          <p className="text-xs text-muted-foreground">
            {content.length} characters • Auto-saves after {autoSaveDelay / 1000}s of inactivity
          </p>
          <Button
            onClick={handleSave}
            disabled={!hasChanges || isSaving}
            size="sm"
            className="gradient-primary"
          >
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Now
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
