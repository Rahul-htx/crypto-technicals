import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import fs from 'fs/promises';
import path from 'path';

interface ThesisData {
  thesis: string;
  updatedAt: string;
  updatedBy: string;
}

const THESIS_FILE = path.join(process.cwd(), 'data', 'thesis.json');

async function loadThesis(): Promise<ThesisData> {
  try {
    const data = await fs.readFile(THESIS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    // Default thesis if file doesn't exist
    return {
      thesis: `# Investment Thesis

## Market Outlook
*Your investment thesis goes here...*

## Key Positions
- Position 1: Rationale
- Position 2: Rationale

## Risk Management
- Risk factor 1
- Risk factor 2`,
      updatedAt: new Date().toISOString(),
      updatedBy: 'system'
    };
  }
}

async function saveThesis(thesis: ThesisData): Promise<void> {
  await fs.mkdir(path.dirname(THESIS_FILE), { recursive: true });
  await fs.writeFile(THESIS_FILE, JSON.stringify(thesis, null, 2));
}

export async function GET(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const thesis = await loadThesis();
    return NextResponse.json(thesis);
  } catch (error) {
    console.error('Thesis GET error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PATCH(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { thesis } = body;

    if (typeof thesis !== 'string') {
      return NextResponse.json(
        { error: 'Invalid thesis format' },
        { status: 400 }
      );
    }

    const thesisData: ThesisData = {
      thesis,
      updatedAt: new Date().toISOString(),
      updatedBy: 'user'
    };

    await saveThesis(thesisData);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Thesis PATCH error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}