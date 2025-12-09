import { RoadmapStep } from '@/api/roadmapApi';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, Clock, Target, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface StepHeaderProps {
  step: RoadmapStep;
  docId: string;
  progress?: number;
  score?: number;
}

export function StepHeader({ step, docId, progress = 0, score }: StepHeaderProps) {
  const navigate = useNavigate();

  return (
    <div className="bg-card border-b sticky top-16 z-30">
      <div className="container mx-auto px-4 py-4 max-w-4xl">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 flex-1 min-w-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(`/roadmap/${docId}`)}
              className="flex-shrink-0"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="min-w-0">
              <p className="text-xs text-muted-foreground font-medium">Step {step.order}</p>
              <h1 className="font-semibold text-lg truncate">{step.title}</h1>
            </div>
          </div>

          <div className="flex items-center gap-6 flex-shrink-0 hidden md:flex">
            <div className="flex items-center gap-2 text-sm">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span>{step.estimatedTime} min</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Target className="h-4 w-4 text-muted-foreground" />
              <span>{step.mcqCount} MCQs</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Zap className="h-4 w-4 text-muted-foreground" />
              <span>{step.flashcardCount} Cards</span>
            </div>
            {score !== undefined && (
              <div className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                Score: {score}%
              </div>
            )}
          </div>
        </div>

        {progress > 0 && (
          <div className="mt-3">
            <Progress value={progress} className="h-1.5" />
          </div>
        )}
      </div>
    </div>
  );
}
