import { RoadmapStep } from '@/api/roadmapApi';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { CheckCircle, Clock, Lock, Play, BookOpen, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

interface RoadmapViewProps {
  steps: RoadmapStep[];
  onStepClick: (step: RoadmapStep) => void;
}

export function RoadmapView({ steps, onStepClick }: RoadmapViewProps) {
  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5" />;
      case 'in_progress': return <Play className="h-5 w-5" />;
      case 'locked': return <Lock className="h-5 w-5" />;
      default: return <BookOpen className="h-5 w-5" />;
    }
  };

  const getStepStyles = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-success text-success-foreground';
      case 'in_progress': return 'gradient-primary text-primary-foreground';
      case 'available': return 'bg-primary/10 text-primary border-2 border-primary';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getConnectorColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-success';
      case 'in_progress': return 'bg-primary';
      default: return 'bg-muted';
    }
  };

  return (
    <div className="relative">
      {steps.map((step, index) => (
        <motion.div
          key={step.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1, duration: 0.3 }}
          className="relative"
        >
          {/* Connector Line */}
          {index < steps.length - 1 && (
            <div className="absolute left-6 top-[4.5rem] w-0.5 h-8 -translate-x-1/2">
              <div className={cn('w-full h-full rounded-full transition-colors', getConnectorColor(step.status))} />
            </div>
          )}
          
          <Card 
            className={cn(
              'mb-4 transition-all cursor-pointer hover:shadow-lg group',
              step.status === 'locked' && 'opacity-60 cursor-not-allowed',
              step.status === 'in_progress' && 'ring-2 ring-primary/50'
            )}
            onClick={() => step.status !== 'locked' && onStepClick(step)}
          >
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                {/* Icon */}
                <div className={cn(
                  'h-12 w-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-105',
                  getStepStyles(step.status)
                )}>
                  {getStepIcon(step.status)}
                </div>
                
                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm text-muted-foreground font-medium">Step {step.order}</span>
                    {step.status === 'in_progress' && (
                      <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full animate-pulse">
                        In Progress
                      </span>
                    )}
                    {step.status === 'completed' && (
                      <span className="text-xs bg-success/10 text-success px-2 py-0.5 rounded-full">
                        Completed
                      </span>
                    )}
                  </div>
                  <h3 className="font-semibold text-lg truncate group-hover:text-primary transition-colors">{step.title}</h3>
                  <p className="text-sm text-muted-foreground line-clamp-2">{step.description}</p>
                </div>
                
                {/* Meta */}
                <div className="text-right flex-shrink-0 hidden sm:block">
                  <p className="text-sm font-medium">
                    {step.mcqCount} MCQs • {step.flashcardCount} Cards
                  </p>
                  <p className="text-xs text-muted-foreground flex items-center justify-end gap-1">
                    <Clock className="h-3 w-3" />
                    {step.estimatedTime} min
                  </p>
                </div>
                
                {/* Action */}
                {step.status !== 'locked' && (
                  <Button 
                    size="sm" 
                    variant={step.status === 'completed' ? 'outline' : 'default'}
                    className={cn(
                      'hidden sm:flex',
                      step.status !== 'completed' && 'gradient-primary'
                    )}
                  >
                    {step.status === 'completed' ? 'Review' : 'Start'}
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Button>
                )}
              </div>
              
              {/* Progress Bar */}
              {step.progress > 0 && step.status !== 'completed' && (
                <div className="mt-4">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium">{step.progress}%</span>
                  </div>
                  <Progress value={step.progress} className="h-1.5" />
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
