import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export default function middleware(request: NextRequest) {
  const isOnDashboard = request.nextUrl.pathname.startsWith("/dashboard");
  const isOnApuntes = request.nextUrl.pathname.startsWith("/apuntes");
  const isOnLogin = request.nextUrl.pathname === "/login";
  const isLoggedIn = request.cookies.has("next-auth.session-token");

  // Si está en login y está autenticado, redirigir a dashboard
  if (isOnLogin && isLoggedIn) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Si está en rutas protegidas y no está autenticado, redirigir a login
  if ((isOnDashboard || isOnApuntes) && !isLoggedIn) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

// Configuración del matcher para las rutas que queremos proteger
export const config = {
  matcher: [
    "/dashboard/:path*",
    "/apuntes/:path*",
    "/login"
  ],
}; 