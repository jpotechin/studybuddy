import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';
import { BookOpen, Plus, Upload, LogOut, Home } from 'lucide-react';

export const Navigation: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  if (!user) return null;

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <BookOpen className="h-6 w-6 text-blue-600" />
              <span className="font-bold text-xl text-gray-900">StudyBuddy</span>
            </Link>
            
            <div className="hidden md:flex space-x-4">
              <Link to="/">
                <Button 
                  variant={isActive('/') ? 'default' : 'ghost'}
                  className="flex items-center space-x-2"
                >
                  <Home className="h-4 w-4" />
                  <span>Study</span>
                </Button>
              </Link>
              
              <Link to="/create">
                <Button 
                  variant={isActive('/create') ? 'default' : 'ghost'}
                  className="flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Create Cards</span>
                </Button>
              </Link>
              
              <Link to="/upload">
                <Button 
                  variant={isActive('/upload') ? 'default' : 'ghost'}
                  className="flex items-center space-x-2"
                >
                  <Upload className="h-4 w-4" />
                  <span>Upload PDF</span>
                </Button>
              </Link>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">Welcome, {user.username}</span>
            <Button variant="outline" onClick={logout} className="flex items-center space-x-2">
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};
