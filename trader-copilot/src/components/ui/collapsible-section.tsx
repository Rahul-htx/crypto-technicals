'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CollapsibleSectionProps {
  title: string;
  description?: string;
  isExpanded?: boolean;
  onExpandedChange?: (expanded: boolean) => void;
  children: React.ReactNode;
  className?: string;
  showInfo?: boolean;
  infoTooltip?: string;
  collapsedPreview?: string; // Optional text to show when collapsed
}

export function CollapsibleSection({
  title,
  description,
  isExpanded = false,
  onExpandedChange,
  children,
  className,
  showInfo = false,
  infoTooltip,
  collapsedPreview
}: CollapsibleSectionProps) {
  const [expanded, setExpanded] = useState(isExpanded);

  useEffect(() => {
    setExpanded(isExpanded);
  }, [isExpanded]);

  const handleToggle = () => {
    const newExpanded = !expanded;
    setExpanded(newExpanded);
    onExpandedChange?.(newExpanded);
  };

  return (
    <Card className={cn("p-4", className)}>
      <div className="space-y-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleToggle}
          className="w-full justify-between p-0 h-auto"
        >
          <div className="flex items-center space-x-2">
            <h3 className="font-medium text-sm">{title}</h3>
            {showInfo && (
              <Info 
                className="h-3 w-3 text-muted-foreground" 
                title={infoTooltip}
              />
            )}
          </div>
          <div className="flex items-center space-x-2">
            {!expanded && collapsedPreview && (
              <span className="text-xs text-muted-foreground max-w-32 truncate">
                {collapsedPreview}
              </span>
            )}
            {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </div>
        </Button>

        {description && !expanded && (
          <p className="text-xs text-muted-foreground">
            {description}
          </p>
        )}

        {expanded && (
          <div className="space-y-3">
            {description && (
              <p className="text-xs text-muted-foreground">
                {description}
              </p>
            )}
            {children}
          </div>
        )}
      </div>
    </Card>
  );
}