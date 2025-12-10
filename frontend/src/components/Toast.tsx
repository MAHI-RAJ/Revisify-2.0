import { useEffect, useState } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  add: (toast: Omit<Toast, 'id'>) => void;
  remove: (id: string) => void;
}

// Simple toast store using a pub/sub pattern
const listeners = new Set<() => void>();
let toasts: Toast[] = [];

function notifyListeners() {
  listeners.forEach(listener => listener());
}

export const toastStore: ToastStore = {
  get toasts() {
    return toasts;
  },
  add: (toast) => {
    const id = Math.random().toString(36).substring(7);
    toasts = [...toasts, { ...toast, id }];
    notifyListeners();
    
    const duration = toast.duration ?? 5000;
    if (duration > 0) {
      setTimeout(() => {
        toastStore.remove(id);
      }, duration);
    }
  },
  remove: (id) => {
    toasts = toasts.filter(t => t.id !== id);
    notifyListeners();
  },
};

export function toast(options: Omit<Toast, 'id'>) {
  toastStore.add(options);
}

export function ToastContainer() {
  const [, forceUpdate] = useState({});

  useEffect(() => {
    const update = () => forceUpdate({});
    listeners.add(update);
    return () => {
      listeners.delete(update);
    };
  }, []);

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  };

  const styles = {
    success: 'bg-success/10 border-success/20 text-success',
    error: 'bg-destructive/10 border-destructive/20 text-destructive',
    warning: 'bg-warning/10 border-warning/20 text-warning',
    info: 'bg-info/10 border-info/20 text-info',
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      <AnimatePresence>
        {toastStore.toasts.map(t => {
          const Icon = icons[t.type];
          return (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, x: 100, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.95 }}
              className={cn(
                'flex items-start gap-3 p-4 rounded-lg border backdrop-blur-sm shadow-lg',
                styles[t.type]
              )}
            >
              <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground">{t.title}</p>
                {t.message && (
                  <p className="text-sm text-muted-foreground mt-1">{t.message}</p>
                )}
              </div>
              <button
                onClick={() => toastStore.remove(t.id)}
                className="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
