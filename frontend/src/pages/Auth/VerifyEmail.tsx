import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '@/state/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, Mail, Loader2, CheckCircle } from 'lucide-react';
import { toast } from '@/components/Toast';

export default function VerifyEmail() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, verifyEmail, resendVerification, isLoading } = useAuthStore();
  const [isResending, setIsResending] = useState(false);
  const token = searchParams.get('token');

  const handleVerify = async () => {
    if (!token) return;
    try {
      await verifyEmail(token);
      toast({ type: 'success', title: 'Email verified!' });
      navigate('/home');
    } catch (err) {
      toast({ type: 'error', title: 'Verification failed', message: 'Invalid or expired token.' });
    }
  };

  const handleResend = async () => {
    if (!user?.email) return;
    setIsResending(true);
    try {
      await resendVerification(user.email);
      toast({ type: 'success', title: 'Verification email sent!' });
    } catch (err) {
      toast({ type: 'error', title: 'Failed to send email' });
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 gradient-hero">
      <Card className="w-full max-w-md animate-scale-in text-center">
        <CardHeader className="space-y-4">
          <div className="mx-auto h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
            <Mail className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl font-bold">Check your email</CardTitle>
          <CardDescription>
            We've sent a verification link to <strong>{user?.email || 'your email'}</strong>
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {token ? (
            <Button onClick={handleVerify} className="w-full gradient-primary" disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <CheckCircle className="mr-2 h-4 w-4" />}
              Verify Email
            </Button>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">
                Click the link in your email to verify your account. If you didn't receive it, click below to resend.
              </p>
              <Button onClick={handleResend} variant="outline" className="w-full" disabled={isResending}>
                {isResending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Resend Verification Email
              </Button>
            </>
          )}
          <Link to="/login" className="block text-sm text-primary hover:underline">
            Back to Login
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
