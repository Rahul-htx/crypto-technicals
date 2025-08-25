'use client';

import { useState, useEffect } from 'react';
import { useSystemStore } from '@/lib/system-context';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { getAuthHeaders } from '@/lib/auth';

// Helper function to format timestamps in CT timezone
function formatTimestamp(isoString: string): string {
  try {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      timeZone: 'America/Chicago',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }) + ' CT';
  } catch {
    return isoString; // Fallback to original if parsing fails
  }
}

// Helper function to format markdown text for thesis display
function formatMarkdown(text: string): string {
  let formatted = text;
  
  // Handle timestamps - convert ISO dates to human readable CT format
  formatted = formatted.replace(/\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?\b/g, (match) => {
    return formatTimestamp(match);
  });
  
  // Handle headers
  formatted = formatted.replace(/^# (.+)$/gm, '<h1 class="text-lg font-bold mb-3 mt-4 first:mt-0">$1</h1>');
  formatted = formatted.replace(/^## (.+)$/gm, '<h2 class="text-base font-semibold mb-2 mt-3">$1</h2>');
  formatted = formatted.replace(/^### (.+)$/gm, '<h3 class="text-sm font-medium mb-2 mt-2">$1</h3>');
  
  // Handle bold text
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>');
  
  // Handle italic text (including underscores)
  formatted = formatted.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
  formatted = formatted.replace(/_(.*?)_/g, '<em class="italic text-muted-foreground">$1</em>');
  
  // Handle line breaks and paragraphs
  const paragraphs = formatted.split(/\n\s*\n/);
  const formattedParagraphs = paragraphs.map(para => {
    const trimmed = para.trim();
    if (!trimmed) return '';
    
    // Skip if already formatted as header
    if (trimmed.startsWith('<h')) return trimmed;
    
    // Convert single line breaks to <br> within paragraphs
    const withBreaks = trimmed.replace(/\n/g, '<br>');
    
    return `<p class="mb-2 leading-relaxed">${withBreaks}</p>`;
  }).filter(Boolean).join('');
  
  return formattedParagraphs;
}

export function ThesisPanel() {
  const { systemCtx, setThesis } = useSystemStore();
  const [editedThesis, setEditedThesis] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [clientFormattedTime, setClientFormattedTime] = useState('');

  useEffect(() => {
    // Load thesis on component mount
    loadThesis();
    
    // Listen for thesis updates from tool calls
    const handleThesisUpdate = () => {
      loadThesis();
    };
    
    window.addEventListener('thesisUpdated', handleThesisUpdate);
    
    return () => {
      window.removeEventListener('thesisUpdated', handleThesisUpdate);
    };
  }, []);

  useEffect(() => {
    // Format timestamp on client-side only to avoid hydration mismatch
    if (systemCtx.updatedAt) {
      setClientFormattedTime(new Date(systemCtx.updatedAt).toLocaleString('en-US', { 
        timeZone: 'America/Chicago',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      }));
    }
  }, [systemCtx.updatedAt]);

  const loadThesis = async () => {
    try {
      const response = await fetch('/api/thesis', {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setThesis(data.thesis, data.updatedBy);
        setEditedThesis(data.thesis);
      }
    } catch (error) {
      console.error('Failed to load thesis:', error);
    }
  };

  const saveThesis = async () => {
    if (editedThesis.trim() === systemCtx.thesis) {
      setIsEditing(false);
      return;
    }

    setIsSaving(true);
    try {
      const response = await fetch('/api/thesis', {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify({ thesis: editedThesis.trim() })
      });

      if (response.ok) {
        setThesis(editedThesis.trim(), 'user');
        setIsEditing(false);
      } else {
        throw new Error('Failed to save thesis');
      }
    } catch (error) {
      console.error('Failed to save thesis:', error);
      // Reset to original
      setEditedThesis(systemCtx.thesis);
    } finally {
      setIsSaving(false);
    }
  };

  const startEditing = () => {
    setEditedThesis(systemCtx.thesis);
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setEditedThesis(systemCtx.thesis);
    setIsEditing(false);
  };

  return (
    <Card className="p-4 mb-4">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="flex items-center space-x-2 p-0 h-auto hover:bg-transparent"
          >
            <h3 className="font-medium text-sm">Investment Thesis</h3>
            {isCollapsed ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronUp className="h-4 w-4" />
            )}
          </Button>
          <div className="flex items-center space-x-2">
            {systemCtx.updatedBy && (
              <Badge variant="secondary" className="text-xs">
                {systemCtx.updatedBy}
              </Badge>
            )}
            {!isEditing && !isCollapsed && (
              <Button variant="ghost" size="sm" onClick={startEditing}>
                Edit
              </Button>
            )}
          </div>
        </div>

        {!isCollapsed && (
          <>
            {isEditing ? (
              <div className="space-y-2">
                <Textarea
                  value={editedThesis}
                  onChange={(e) => setEditedThesis(e.target.value)}
                  placeholder="Enter your investment thesis..."
                  className="min-h-[200px] text-sm"
                />
                <div className="flex space-x-2">
                  <Button size="sm" onClick={saveThesis} disabled={isSaving}>
                    {isSaving ? 'Saving...' : 'Save'}
                  </Button>
                  <Button variant="ghost" size="sm" onClick={cancelEditing}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-sm">
                {systemCtx.thesis ? (
                  <div 
                    className="bg-muted/30 p-3 rounded-lg"
                    dangerouslySetInnerHTML={{ 
                      __html: formatMarkdown(systemCtx.thesis) 
                    }}
                  />
                ) : (
                  <p className="text-muted-foreground text-sm">
                    No thesis available. Click Edit to set one.
                  </p>
                )}
              </div>
            )}

            {clientFormattedTime && (
              <p className="text-xs text-muted-foreground">
                Updated: {clientFormattedTime} CT
              </p>
            )}
          </>
        )}
      </div>
    </Card>
  );
}