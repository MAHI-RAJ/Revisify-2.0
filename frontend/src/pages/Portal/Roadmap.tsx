import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDocStore } from '@/state/docStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Loader } from '@/components/Loader';
import { RoadmapView } from '@/components/RoadmapView';
import { RoadmapMiniMap } from '@/components/RoadmapMiniMap';
import { Clock, MessageSquare, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Roadmap() {
  const { docId } = useParams<{ docId: string }>();
  const navigate = useNavigate();
  const { currentRoadmap, fetchRoadmap, isLoading, error } = useDocStore();

  useEffect(() => {
    if (docId) fetchRoadmap(docId);
  }, [docId, fetchRoadmap]);

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader size="lg" text="Loading roadmap..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <Card className="max-w-md mx-auto">
          <CardContent className="py-12">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => navigate('/home')} variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!currentRoadmap) return null;

  const overallProgress = Math.round((currentRoadmap.completedSteps / currentRoadmap.totalSteps) * 100);

  const handleStepClick = (step: any) => {
    navigate(`/learn/${step.id}`);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Mini Map */}
      <RoadmapMiniMap
        steps={currentRoadmap.steps}
        onStepClick={handleStepClick}
      />

      {/* Header Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Card className="mb-8 overflow-hidden">
          <div className="gradient-primary h-2" />
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <CardTitle className="text-2xl mb-2">{currentRoadmap.title}</CardTitle>
                <CardDescription className="text-base">{currentRoadmap.description}</CardDescription>
              </div>
              {docId && (
                <Button
                  variant="outline"
                  onClick={() => navigate(`/ask/${docId}`)}
                  className="flex-shrink-0"
                >
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Ask AI
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-3">
              <div className="flex items-center gap-4">
                <span className="text-sm text-muted-foreground">
                  {currentRoadmap.completedSteps} of {currentRoadmap.totalSteps} steps completed
                </span>
                <span className="text-sm text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {Math.round(currentRoadmap.estimatedTotalTime / 60)}h {currentRoadmap.estimatedTotalTime % 60}m total
                </span>
              </div>
              <span className="text-xl font-bold text-primary">{overallProgress}%</span>
            </div>
            <Progress value={overallProgress} className="h-3" />
          </CardContent>
        </Card>
      </motion.div>

      {/* Roadmap Steps */}
      <RoadmapView
        steps={currentRoadmap.steps}
        onStepClick={handleStepClick}
      />
    </div>
  );
}
