import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { ToastContainer } from "@/components/Toast";

// Auth Pages
import Login from "@/pages/Auth/Login";
import Signup from "@/pages/Auth/Signup";
import VerifyEmail from "@/pages/Auth/VerifyEmail";

// Portal Pages
import Home from "@/pages/Portal/Home";
import Upload from "@/pages/Portal/Upload";
import Processing from "@/pages/Portal/Processing";
import Roadmap from "@/pages/Portal/Roadmap";
import LearnStep from "@/pages/Portal/LearnStep";
import AskDoc from "@/pages/Portal/AskDoc";
import Dashboard from "@/pages/Portal/Dashboard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <ToastContainer />
      <BrowserRouter>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/verify-email" element={<VerifyEmail />} />

              {/* Protected Routes */}
              <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
              <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
              <Route path="/processing/:docId" element={<ProtectedRoute><Processing /></ProtectedRoute>} />
              <Route path="/roadmap/:docId" element={<ProtectedRoute><Roadmap /></ProtectedRoute>} />
              <Route path="/learn/:stepId" element={<ProtectedRoute><LearnStep /></ProtectedRoute>} />
              <Route path="/ask/:docId" element={<ProtectedRoute><AskDoc /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

              {/* Catch-all */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
