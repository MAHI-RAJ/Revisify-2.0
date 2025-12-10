import { Hint } from '@/api/tutorApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lightbulb, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface HintPanelProps {
  hints: Hint[];
  onRequestHint: () => void;
  isLoading?: boolean;
  maxHints?: number;
}

export function HintPanel({ hints, onRequestHint, isLoading = false, maxHints = 3 }: HintPanelProps) {
  const canRequestMore = hints.length < maxHints;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Lightbulb className="h-5 w-5 text-warning" />
          Hints
          <span className="text-sm font-normal text-muted-foreground ml-auto">
            {hints.length}/{maxHints} used
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <AnimatePresence>
          {hints.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              Stuck? Click below to get a hint!
            </p>
          ) : (
            hints.map((hint, index) => (
              <motion.div
                key={hint.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 rounded-xl bg-warning/10 border border-warning/20"
              >
                <div className="flex items-start gap-2">
                  <span className="h-6 w-6 rounded-full bg-warning/20 flex items-center justify-center text-xs font-medium text-warning flex-shrink-0">
                    {index + 1}
                  </span>
                  <p className="text-sm">{hint.content}</p>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>

        <Button
          onClick={onRequestHint}
          disabled={!canRequestMore || isLoading}
          variant="outline"
          className="w-full"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Getting hint...
            </>
          ) : canRequestMore ? (
            <>
              <Lightbulb className="mr-2 h-4 w-4" />
              Get Hint ({maxHints - hints.length} remaining)
            </>
          ) : (
            'No more hints available'
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
