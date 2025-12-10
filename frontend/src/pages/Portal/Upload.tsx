import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDocStore } from '@/state/docStore';
import { FileUploader } from '@/components/FileUploader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from '@/components/Toast';
import { Sparkles } from 'lucide-react';

export default function Upload() {
  const navigate = useNavigate();
  const { uploadDocument, uploadProgress, isLoading } = useDocStore();

  const handleUpload = async (file: File) => {
    try {
      const doc = await uploadDocument(file);
      toast({ type: 'success', title: 'Upload successful!', message: 'Processing your document...' });
      navigate(`/processing/${doc.id}`);
    } catch (err: any) {
      toast({ type: 'error', title: 'Upload failed', message: err.response?.data?.message || 'Please try again.' });
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card className="animate-fade-in">
        <CardHeader className="text-center">
          <div className="mx-auto h-14 w-14 rounded-2xl gradient-primary flex items-center justify-center shadow-glow mb-4">
            <Sparkles className="h-7 w-7 text-primary-foreground" />
          </div>
          <CardTitle className="text-2xl">Upload Your Document</CardTitle>
          <CardDescription>Upload a PDF or Word document to generate an AI-powered learning roadmap</CardDescription>
        </CardHeader>
        <CardContent>
          <FileUploader
            onUpload={handleUpload}
            progress={uploadProgress?.percentage}
            isUploading={isLoading}
          />
        </CardContent>
      </Card>
    </div>
  );
}
