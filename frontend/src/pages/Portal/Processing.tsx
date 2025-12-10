import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDocStore } from '@/state/docStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Loader2, CheckCircle, FileText, Brain, Map, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

const steps = [
  { id: 'upload', label: 'Document Uploaded', icon: FileText },
  { id: 'analyze', label: 'Analyzing Content', icon: Brain },
  { id: 'roadmap', label: 'Generating Roadmap', icon: Map },
  { id: 'complete', label: 'Ready to Learn', icon: Sparkles },
];

export default function Processing() {
  const { docId } = useParams<{ docId: string }>();
  const navigate = useNavigate();
  const { currentDocument, fetchDocument, pollDocumentStatus } = useDocStore();
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (docId) fetchDocument(docId);
  }, [docId, fetchDocument]);

  useEffect(() => {
    if (!docId) return;
    
    const interval = setInterval(async () => {
      try {
        const doc = await pollDocumentStatus(docId);
        setProgress(doc.progress);
        
        if (doc.progress < 25) setCurrentStep(0);
        else if (doc.progress < 50) setCurrentStep(1);
        else if (doc.progress < 100) setCurrentStep(2);
        else setCurrentStep(3);

        if (doc.status === 'ready') {
          clearInterval(interval);
          setTimeout(() => navigate(`/roadmap/${docId}`), 1500);
        }
        if (doc.status === 'failed') {
          clearInterval(interval);
        }
      } catch (err) {
        // Keep polling
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [docId, pollDocumentStatus, navigate]);

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card className="animate-fade-in">
        <CardHeader className="text-center">
          <div className="mx-auto h-16 w-16 rounded-full gradient-primary flex items-center justify-center shadow-glow mb-4">
            <Loader2 className="h-8 w-8 text-primary-foreground animate-spin" />
          </div>
          <CardTitle className="text-2xl">Processing Your Document</CardTitle>
          <CardDescription>{currentDocument?.title || 'Please wait...'}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-8">
          <div className="space-y-2">
            <Progress value={progress} className="h-3" />
            <p className="text-sm text-muted-foreground text-center">{progress}% complete</p>
          </div>

          <div className="space-y-4">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = index === currentStep;
              const isComplete = index < currentStep;
              
              return (
                <div key={step.id} className={cn(
                  'flex items-center gap-4 p-4 rounded-lg transition-all',
                  isActive && 'bg-primary/10',
                  isComplete && 'opacity-60'
                )}>
                  <div className={cn(
                    'h-10 w-10 rounded-full flex items-center justify-center transition-all',
                    isComplete ? 'bg-success text-success-foreground' : isActive ? 'gradient-primary text-primary-foreground' : 'bg-muted'
                  )}>
                    {isComplete ? <CheckCircle className="h-5 w-5" /> : <Icon className={cn('h-5 w-5', isActive && 'animate-pulse')} />}
                  </div>
                  <span className={cn('font-medium', isActive && 'text-primary')}>{step.label}</span>
                  {isActive && <Loader2 className="h-4 w-4 animate-spin ml-auto text-primary" />}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
