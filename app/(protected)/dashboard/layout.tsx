"use client";
import { useState } from "react";
import { DashboardNav } from "@/components/dashboard/dashboard-nav";
import MobileBottomNavWrapper from "@/components/MobileBottomNavWrapper";
import { Player } from "@lottiefiles/react-lottie-player";
import { DayPicker } from "react-day-picker";
import "react-day-picker/dist/style.css";

// Add Google Fonts in _document.js or <Head> in your app for 'EB Garamond' and 'Inter'
// <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@700&family=Inter:wght@400;600&display=swap" rel="stylesheet" />

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [theme, setTheme] = useState("light");
  const [selected, setSelected] = useState();
  const toggleTheme = () => setTheme(theme === "light" ? "dark" : "light");

  const palette = theme === "light"
    ? {
        bg: "#F8FAFF",
        card: "#FFFFFF",
        header: "#FFFFFF",
        border: "#232346",
        text: "#232346",
        accent: "#00E6A0",
        primary: "#6C63FF",
        blue: "#00CFFF",
        pink: "#FF5A7A",
        btn: "#232346",
        btnHover: "#6C63FF",
      }
    : {
        bg: "#181830",
        card: "#232346",
        header: "#232346",
        border: "#E0E0FF",
        text: "#E0E0FF",
        accent: "#00E6A0",
        primary: "#6C63FF",
        blue: "#00CFFF",
        pink: "#FF5A7A",
        btn: "#E0E0FF",
        btnHover: "#FF5A7A",
      };

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{
        background: palette.bg,
        color: palette.text,
        fontFamily: "'Inter', 'EB Garamond', serif",
      }}
    >
      <header
        className="sticky top-0 z-40 border-b"
        style={{
          background: palette.header,
          borderColor: palette.border,
        }}
      >
        <div className="container flex h-20 items-center justify-between py-4">
          <DashboardNav />
          <button
            onClick={toggleTheme}
            className="ml-4 px-6 py-2 rounded-full font-bold shadow-md transition-colors duration-200 border-2 border-black tracking-widest uppercase"
            style={{
              background: palette.btn,
              color: theme === "light" ? "#fff" : "#232346",
              letterSpacing: "0.2em",
              fontFamily: "'EB Garamond', serif",
              fontSize: "1.1rem",
            }}
          >
            {theme === "light" ? "🌙 Vogue" : "☀️ Vogue"}
          </button>
        </div>
      </header>
      <main className="container flex-1 py-12">
        {/* Lottie Animation */}
        <div className="flex justify-center mb-8">
          <Player
            autoplay
            loop
            src="https://assets2.lottiefiles.com/packages/lf20_5ngs2ksb.json"
            style={{ height: "180px", width: "180px" }}
          />
        </div>
        {/* Date Picker */}
        <div className="flex justify-center mb-8">
          <DayPicker
            mode="single"
            selected={selected}
            onSelect={setSelected}
            styles={{
              caption: { color: palette.primary, fontFamily: "'EB Garamond', serif", fontWeight: 700, fontSize: "1.2rem" },
              day_selected: { backgroundColor: palette.accent, color: '#fff' },
              day_today: { borderColor: palette.primary },
            }}
          />
        </div>
        {/* Main Card */}
        <div
          className="mb-12 p-10 rounded-3xl shadow-lg border"
          style={{
            background: palette.card,
            borderColor: palette.border,
            fontFamily: "'EB Garamond', serif",
          }}
        >
          <h2 className="text-5xl md:text-6xl font-extrabold mb-4 tracking-tight uppercase" style={{ color: palette.primary, letterSpacing: "0.08em" }}>
            Panel de Control
          </h2>
          <div className="border-b-2 border-black w-24 mb-6"></div>
          <p className="text-2xl mb-6" style={{ color: palette.blue, fontFamily: "'Inter', sans-serif" }}>
            Gestiona tus cursos, progreso y más.
          </p>
          <button
            className="mt-2 px-8 py-3 rounded-full font-bold shadow-md transition-colors duration-200 border-2 border-black tracking-widest uppercase"
            style={{
              background: palette.btn,
              color: theme === "light" ? "#fff" : "#232346",
              letterSpacing: "0.2em",
              fontFamily: "'EB Garamond', serif",
              fontSize: "1.1rem",
            }}
            onMouseOver={e => (e.currentTarget.style.background = palette.btnHover)}
            onMouseOut={e => (e.currentTarget.style.background = palette.btn)}
          >
            Nuevo Curso
          </button>
        </div>
        {/* Grid Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div
            className="p-8 rounded-3xl shadow border flex flex-col justify-between"
            style={{
              background: palette.card,
              borderColor: palette.border,
              fontFamily: "'EB Garamond', serif",
            }}
          >
            <h3 className="text-3xl font-bold mb-4 uppercase tracking-widest" style={{ color: palette.primary }}>
              Tus Cursos
            </h3>
            <p className="text-lg" style={{ color: palette.blue, fontFamily: "'Inter', sans-serif" }}>
              Visualiza y accede a tus cursos activos.
            </p>
          </div>
          <div
            className="p-8 rounded-3xl shadow border flex flex-col justify-between"
            style={{
              background: palette.card,
              borderColor: palette.border,
              fontFamily: "'EB Garamond', serif",
            }}
          >
            <h3 className="text-3xl font-bold mb-4 uppercase tracking-widest" style={{ color: palette.primary }}>
              Progreso
            </h3>
            <p className="text-lg" style={{ color: palette.blue, fontFamily: "'Inter', sans-serif" }}>
              Revisa tu avance y logros recientes.
            </p>
          </div>
      </div>
        <div className="mt-12">{children}</div>
      </main>
      <MobileBottomNavWrapper />
    </div>
  );
} 