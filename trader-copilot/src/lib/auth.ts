import { NextRequest } from 'next/server';

export function verifyAuth(request: NextRequest): boolean {
  const authHeader = request.headers.get('authorization');
  const expectedToken = process.env.BASIC_AUTH_TOKEN;

  if (!expectedToken) {
    console.warn('BASIC_AUTH_TOKEN not configured');
    return false;
  }

  if (!authHeader) {
    return false;
  }

  // Expected format: "Bearer dev-secret"
  const [scheme, token] = authHeader.split(' ');
  
  if (scheme !== 'Bearer' || token !== expectedToken) {
    return false;
  }

  return true;
}

export function getAuthHeaders(): HeadersInit {
  // For client-side use, we'll use the default dev token
  // In production, this should be handled differently (e.g., from a secure cookie)
  const token = 'dev-secret';
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}