import { RoadmapStep } from '@/api/roadmapApi';
import { cn } from '@/lib/utils';
import { CheckCircle, Lock, Play, Circle } from 'lucide-react';

interface RoadmapMiniMapProps {
  steps: RoadmapStep[];
  currentStepId?: string;
  onStepClick: (step: RoadmapStep) => void;
}

export function RoadmapMiniMap({ steps, currentStepId, onStepClick }: RoadmapMiniMapProps) {
  const getStepIcon = (status: string, isActive: boolean) => {
    if (status === 'completed') return <CheckCircle className="h-3 w-3" />;
    if (status === 'locked') return <Lock className="h-3 w-3" />;
    if (isActive || status === 'in_progress') return <Play className="h-3 w-3" />;
    return <Circle className="h-3 w-3" />;
  };

  const getStepColor = (status: string, isActive: boolean) => {
    if (isActive) return 'bg-primary text-primary-foreground ring-2 ring-primary ring-offset-2';
    switch (status) {
      case 'completed': return 'bg-success text-success-foreground';
      case 'in_progress': return 'bg-primary/80 text-primary-foreground';
      case 'available': return 'bg-primary/20 text-primary hover:bg-primary/30';
      default: return 'bg-muted text-muted-foreground cursor-not-allowed';
    }
  };

  return (
    <div className="fixed top-24 right-4 z-40 hidden xl:block">
      <div className="bg-card/95 backdrop-blur-sm border rounded-xl p-4 shadow-lg w-48">
        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Progress</h4>
        <div className="space-y-2">
          {steps.map((step, index) => {
            const isActive = step.id === currentStepId;
            return (
              <button
                key={step.id}
                onClick={() => step.status !== 'locked' && onStepClick(step)}
                disabled={step.status === 'locked'}
                className={cn(
                  'w-full flex items-center gap-2 p-2 rounded-lg text-left transition-all text-xs',
                  getStepColor(step.status, isActive)
                )}
              >
                <span className="flex items-center justify-center h-5 w-5 rounded-full bg-background/20">
                  {getStepIcon(step.status, isActive)}
                </span>
                <span className="truncate flex-1">{step.title}</span>
                {step.status === 'completed' && (
                  <span className="text-[10px] opacity-70">✓</span>
                )}
              </button>
            );
          })}
        </div>
        <div className="mt-4 pt-3 border-t">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Completed</span>
            <span className="font-medium">{steps.filter(s => s.status === 'completed').length}/{steps.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
