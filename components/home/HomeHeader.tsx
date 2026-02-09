"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { NAV_LINKS, PROFILE_MENU_LINKS } from "@/app/home/constants";

export function HomeHeader() {
  const [isProfileOpen, setIsProfileOpen] = React.useState(false);
  const router = useRouter();

  const handleSignOut = async () => {
    try {
      await signOut({
        callbackUrl: "/",
        redirect: true,
      });
      setIsProfileOpen(false);
    } catch (error) {
      console.error("Error signing out:", error);
      router.push("/");
    }
  };

  return (
    <header className="w-full bg-white shadow-none border-b border-[#E3D6FF] sticky top-0 z-50 flex items-center justify-between px-8 py-6">
      <Link href="/" className="flex items-center group">
        <Image src="/b_logo.png" alt="b logo" width={64} height={64} className="h-16 w-16" />
      </Link>
      <nav className="hidden md:flex gap-10 mx-auto">
        {NAV_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="text-black hover:text-[#A259FF] transition-colors font-medium"
          >
            {link.label}
          </Link>
        ))}
      </nav>
      <div className="flex items-center gap-6">
        <Link
          href="/login"
          className="hidden md:block text-black hover:text-[#A259FF] transition-colors font-medium"
        >
          Iniciar Sesión
        </Link>
        <Link
          href="/register"
          className="hidden md:block px-6 py-2 bg-black text-white rounded-full hover:bg-[#A259FF] transition-colors font-medium"
        >
          Registrarse
        </Link>

        <div className="relative">
          <button
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[#FFD6E3] to-[#E3D6FF] flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" />
                <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" />
              </svg>
            </div>
          </button>
          {isProfileOpen && (
            <div
              className="absolute right-0 mt-4 w-80 bg-white text-black rounded-2xl shadow-2xl border-4 border-[#E3D6FF] py-6 z-50"
              style={{ boxShadow: "0 8px 40px 0 #E3D6FF66" }}
            >
              <div className="px-8 py-5 border-b-2 border-[#E3D6FF]">
                <p className="text-base text-[#6B6B8D]">Bienvenido a</p>
                <p className="font-bold text-2xl text-black">Tu Cuenta</p>
              </div>
              <nav className="px-4 py-4">
                {PROFILE_MENU_LINKS.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="flex items-center gap-4 px-5 py-4 text-black hover:bg-[#FFD6E3] rounded-xl transition-colors duration-200 mb-2 font-semibold text-lg"
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#A259FF" strokeWidth="2">
                      <path d={link.icon} />
                    </svg>
                    {link.label}
                  </Link>
                ))}
              </nav>
              <div className="border-t-2 border-[#E3D6FF] mx-4 my-2"></div>
              <div className="px-4 py-4">
                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center justify-center gap-3 px-5 py-4 text-red-600 hover:bg-[#FFD6E3] rounded-xl transition-colors duration-200 font-semibold text-lg"
                  aria-label="Cerrar sesión"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#A259FF" strokeWidth="2">
                    <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Cerrar Sesión
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}















