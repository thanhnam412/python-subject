import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const { email, password, username } = await req?.json();
  const origin = req.headers.get("origin");
  if (origin !== "http://localhost:3000") {
    return NextResponse.json({ error: "Unauthorized origin" }, { status: 403 });
  }

  let backendRes
  try {
    backendRes = await fetch('http://localhost:8080/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, username }),
    });
  } catch (e) {
    console.log(e)
  }

  if (backendRes && !backendRes.ok) {
    return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });
  }

  const data = await backendRes?.json();

  const token = data.access_token;

  const response = NextResponse.json({ success: true, data: data.user });

  response.cookies.set('access_token_cookie', token, {
    httpOnly: true,
    sameSite: 'strict',
    path: '/',
    maxAge: 60 * 5
  });

  const setCookieHeader = backendRes?.headers.get('set-cookie');
  let csrfToken = null;

  if (setCookieHeader) {
    const cookies = setCookieHeader.split(',').map(cookie => cookie.trim());
    for (const cookie of cookies) {
      if (cookie.startsWith('csrf_token_cookie=')) {
        csrfToken = cookie.split(';')[0].split('=')[1]
        break;
      }
    }
  }

  if (csrfToken) {
    response.cookies.set('csrf_token_cookie', csrfToken, {
      httpOnly: true,
      sameSite: 'strict',
      path: '/',
      maxAge: 60 * 5
    });
  }

  return response;
}
