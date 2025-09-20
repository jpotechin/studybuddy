import React, { useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { useAuth } from '../contexts/AuthContext';
import { Upload, FileText, AlertCircle } from 'lucide-react';

export const UploadPDF: React.FC = () => {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [subject, setSubject] = useState('');
  const [test, setTest] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file || !subject.trim() || !test.trim()) {
      setError('Please select a file and fill in subject and test fields');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('subject', subject.trim());
      formData.append('test', test.trim());

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/upload_pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setUploadResult(result.message);
      
      // Reset form
      setFile(null);
      setSubject('');
      setTest('');
      
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload PDF</h1>
        <p className="text-gray-600">
          Upload a PDF file to automatically generate flashcards using AI
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload PDF Document</CardTitle>
          <CardDescription>
            Select a PDF file and specify the subject and test name
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File Upload */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              PDF File
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="file-input" className="cursor-pointer">
                {file ? (
                  <div className="flex items-center justify-center space-x-2 text-green-600">
                    <FileText className="h-8 w-8" />
                    <span className="font-medium">{file.name}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center space-y-2 text-gray-500">
                    <Upload className="h-8 w-8" />
                    <span>Click to select PDF file</span>
                    <span className="text-sm">or drag and drop</span>
                  </div>
                )}
              </label>
            </div>
          </div>

          {/* Subject and Test Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Subject
              </label>
              <Input
                placeholder="e.g., CSC280"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Test
              </label>
              <Input
                placeholder="e.g., Test1"
                value={test}
                onChange={(e) => setTest(e.target.value)}
              />
            </div>
          </div>

          {/* Upload Button */}
          <Button 
            onClick={handleUpload} 
            disabled={!file || !subject.trim() || !test.trim() || isUploading}
            className="w-full"
            size="lg"
          >
            {isUploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processing PDF...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Generate Flashcards
              </>
            )}
          </Button>

          {/* Results */}
          {uploadResult && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2 text-green-800">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="font-medium">Success!</span>
              </div>
              <p className="text-green-700 mt-1">{uploadResult}</p>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2 text-red-800">
                <AlertCircle className="h-4 w-4" />
                <span className="font-medium">Error</span>
              </div>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
