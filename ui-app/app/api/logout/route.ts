import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function POST() {
  try {
    const res = await fetch('http://localhost:8080/auth/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!res.ok) {
      throw new Error('Logout failed from backend');
    }

    const response = NextResponse.json({ message: 'Logged out successfully' });

    const cookieStore = await cookies();


    cookieStore.set({
      name: 'access_token_cookie',
      value: '',
      path: '/',
      httpOnly: true,
      sameSite: 'strict',
      secure: true
    });

    cookieStore.set({
      name: 'csrf_token_cookie',
      value: '',
      path: '/',
      httpOnly: true,
      sameSite: 'strict',
      secure: true
    });

    return response;
  } catch (err) {
    console.error('Logout error:', err);
    return NextResponse.json({ error: 'Logout failed' }, { status: 500 });
  }
}
