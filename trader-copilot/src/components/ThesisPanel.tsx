'use client';

import { useState, useEffect } from 'react';
import { useSystemStore } from '@/lib/system-context';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { getAuthHeaders } from '@/lib/auth';

export function ThesisPanel() {
  const { systemCtx, setThesis } = useSystemStore();
  const [editedThesis, setEditedThesis] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [clientFormattedTime, setClientFormattedTime] = useState('');

  useEffect(() => {
    // Load thesis on component mount
    loadThesis();
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
          <h3 className="font-medium text-sm">Investment Thesis</h3>
          <div className="flex items-center space-x-2">
            {systemCtx.updatedBy && (
              <Badge variant="secondary" className="text-xs">
                {systemCtx.updatedBy}
              </Badge>
            )}
            {!isEditing && (
              <Button variant="ghost" size="sm" onClick={startEditing}>
                Edit
              </Button>
            )}
          </div>
        </div>

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
          <div className="prose prose-sm max-w-none">
            {systemCtx.thesis ? (
              <pre className="whitespace-pre-wrap text-xs font-mono bg-muted p-3 rounded">
                {systemCtx.thesis}
              </pre>
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
      </div>
    </Card>
  );
}