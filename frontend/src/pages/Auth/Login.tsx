import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/state/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, Mail, Lock, Loader2 } from 'lucide-react';
import { toast } from '@/components/Toast';

export default function Login() {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    try {
      await login({ email, password });
      toast({ type: 'success', title: 'Welcome back!' });
      navigate('/home');
    } catch (err: any) {
      toast({ type: 'error', title: 'Login failed', message: err.response?.data?.message || 'Please check your credentials.' });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 gradient-hero">
      <Card className="w-full max-w-md animate-scale-in">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto h-14 w-14 rounded-2xl gradient-primary flex items-center justify-center shadow-glow">
            <BookOpen className="h-7 w-7 text-primary-foreground" />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold">Welcome back</CardTitle>
            <CardDescription>Sign in to continue your learning journey</CardDescription>
          </div>
        </CardHeader>
        
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10"
                  required
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            {error && (
              <p className="text-sm text-destructive animate-fade-in">{error}</p>
            )}
          </CardContent>
          
          <CardFooter className="flex flex-col gap-4">
            <Button type="submit" className="w-full gradient-primary" disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Sign In
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              Don't have an account?{' '}
              <Link to="/signup" className="text-primary hover:underline font-medium">
                Sign up
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
