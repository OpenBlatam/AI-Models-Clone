"use client";
import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import Image from "next/image";
import LogoMarquee from "@/components/LogoMarquee";
import { signIn } from "next-auth/react";
import "@/styles/globals.css";
// Si tienes componentes Header y Footer personalizados, impórtalos aquí:
// import Header from "@/components/Header";
// import Footer from "@/components/Footer";

const companyLogos = [
  { src: "/logos/santander.png", alt: "Santander" },
  { src: "/logos/att.png", alt: "AT&T" },
  { src: "/logos/accenture.png", alt: "Accenture" },
  { src: "/logos/softtek.png", alt: "Softtek" },
  { src: "/logos/kueski.png", alt: "Kueski" },
  // Puedes agregar más logos locales aquí
];

export default function HomePage() {
  return (
    <>
      {/* Modern Navbar Header SOLO en la página principal */}
      <header className="w-full bg-white shadow-none border-b border-[#E3D6FF] sticky top-0 z-50 flex items-center justify-between px-8 py-6">
        <Link href="/" className="flex items-center group">
          <Image src="/b_logo.png" alt="b logo" width={64} height={64} className="h-16 w-16" />
        </Link>
        <nav className="hidden md:flex gap-10 mx-auto">
          {[
            { href: "/pricing", label: "Pricing" },
            { href: "/features", label: "Features" },
            { href: "/enterprise", label: "Enterprise" },
            { href: "/blog", label: "Blog" },
            { href: "/forum", label: "Forum" },
            { href: "/careers", label: "Careers" },
          ].map(link => (
            <Link
              key={link.href}
              href={link.href}
              className="relative text-gray-700 font-semibold hover:text-[#FFD700] transition-colors px-2 py-1 border-b-2 border-transparent hover:border-[#FFD700]"
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="hidden md:block h-8 w-px bg-[#E3D6FF] mx-4" />
        <div className="flex gap-2">
          <button
            className="px-6 py-2 rounded-full border-2 border-[#E3D6FF] bg-white text-black font-bold uppercase tracking-widest hover:bg-[#F3F7FF] hover:text-[#A259FF] transition"
            onClick={() => window.location.href = "/login"}
          >
            Sign in
          </button>
          <button
            className="px-6 py-2 rounded-full border-2 border-black bg-white text-black font-bold uppercase tracking-widest hover:bg-black hover:text-white transition"
            onClick={() => signIn("google")}
          >
            Sign up
          </button>
        </div>
      </header>
      <main className="min-h-screen flex flex-col items-center justify-center px-4 py-20 w-full" style={{background: 'linear-gradient(135deg, #F3F7FF 0%, #E3D6FF 100%)'}}>
        {/* Hero section */}
        <div className="flex flex-col items-center justify-center py-32 w-full">
          {/* Da Vinci spiral icon */}
          <div className="mb-6">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none"><path d="M24 24c0-8 8-8 8 0s-8 8-8 0zm0 0c0-12 12-12 12 0s-12 12-12 0zm0 0c0-16 16-16 16 0s-16 16-16 0z" stroke="#FFD700" strokeWidth="2" fill="none"/></svg>
          </div>
          <span className="inline-block px-6 py-2 rounded-full border-2" style={{borderColor: '#E3D6FF', background: '#fff', color: '#A259FF', fontWeight: 700, fontSize: '1.1rem', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '2rem', fontStyle: 'italic'}}>
            The Everything App for Marketers
          </span>
          <h1 className="text-5xl md:text-6xl font-serif font-extrabold italic text-black tracking-tight leading-tight uppercase mb-8 animate-fadein">
            The Everything AI Marketing,<br />
            <span style={{background: 'linear-gradient(90deg, #FFD6E3 0%, #E3D6FF 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', display: 'inline-block'}}>
              for teams that create
            </span>
          </h1>
          <p className="text-2xl text-center text-neutral-700 mb-12 max-w-3xl font-light">
            All your marketing, content, and creative work—brainstormed, designed, written, and launched in one place. For every team, every campaign, every idea. All powered by AI.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center w-full max-w-lg">
            <a href="/trial" className="px-12 py-5 rounded-3xl font-extrabold text-2xl shadow-2xl transition-transform duration-200 hover:scale-105 border-0" style={{background: 'linear-gradient(90deg, #FFD6E3 0%, #E3D6FF 100%)', color: '#23235F', boxShadow: '0 4px 24px 0 #FFD70022', letterSpacing: '0.02em'}}>Try b Free</a>
            <a href="/demo" className="px-12 py-5 rounded-3xl font-extrabold text-2xl border-2 border-black bg-white text-black hover:bg-black hover:text-white transition">See It in Action</a>
          </div>
        </div>

        {/* Línea divisoria dorada sutil */}
        <div className="w-full h-0.5 my-16" style={{background: 'linear-gradient(90deg, #fff 0%, #FFD700 50%, #fff 100%)', opacity: 0.18}} />

        {/* Fragmented AI vs All-in-One Solution Section */}
        <section className="w-full max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-20 py-24 px-4">
          {/* Left: Problem */}
          <div className="bg-white rounded-3xl p-14 flex flex-col items-center border-2 border-[#E3D6FF]" style={{ boxShadow: '0 2px 8px 0 #E3D6FF22' }}>
            <h2 className="text-5xl font-extrabold mb-8 text-black tracking-widest uppercase font-serif italic">AI for marketing is fragmented.</h2>
            <p className="text-xl mb-10 text-center text-neutral-700 font-light">
              Jumping between OpusClip, b, HeyGen, Blaze AI, and more? App-switching slows you down, breaks your flow, and makes creative work harder than it should be.
            </p>
            <div className="flex flex-wrap gap-8 justify-center">
              <img src="/logos/opusclip.png" alt="OpusClip" className="h-14 rounded-2xl bg-white p-4 border-2 border-[#E3D6FF]" />
              <img src="/logos/b.png" alt="b" className="h-14 rounded-2xl bg-white p-4 border-2 border-[#E3D6FF]" />
              <img src="/logos/heygen.png" alt="HeyGen" className="h-14 rounded-2xl bg-white p-4 border-2 border-[#E3D6FF]" />
              <img src="/logos/blazeai.png" alt="Blaze AI" className="h-14 rounded-2xl bg-white p-4 border-2 border-[#E3D6FF]" />
            </div>
          </div>

          {/* Right: Solution */}
          <div className="bg-white rounded-3xl p-14 flex flex-col items-center border-2 border-[#E3D6FF]" style={{ boxShadow: '0 2px 8px 0 #FFD70011' }}>
            <h2 className="text-5xl font-extrabold mb-8 text-black tracking-widest uppercase font-serif italic">Let's fix it.</h2>
            <p className="text-xl mb-10 text-center text-neutral-700 font-light">
              Meet the everything AI marketing platform. All your creative, content, and campaign tools—together in one magical workspace. No more switching. Just flow.
            </p>
            <a
              href="/trial"
              className="px-12 py-5 rounded-3xl font-extrabold text-2xl shadow-2xl transition-transform duration-200 hover:scale-105 border-0" style={{background: 'linear-gradient(90deg, #FFD6E3 0%, #E3D6FF 100%)', color: '#23235F', boxShadow: '0 4px 24px 0 #FFD70022', letterSpacing: '0.02em'}}>Get started. It's FREE!</a>
            <p className="text-center font-medium mt-4 text-neutral-500 text-lg">
              Free Forever. No Credit Card.
            </p>
          </div>
        </section>

        {/* Sección editorial Vogue */}
        <section className="w-full bg-black text-white py-24 px-8 text-center my-24 rounded-3xl">
          <h2 className="text-7xl font-serif italic font-extrabold mb-8 tracking-tight">Unleash Your Creativity</h2>
          <p className="text-2xl font-light max-w-3xl mx-auto">Vogue-level marketing for brands that want to stand out. <span className="text-[#FFD700] font-bold">Luxury. Editorial. Impact.</span></p>
        </section>

        {/* Cursos destacados */}
        <section className="mt-20 w-full max-w-5xl">
          <h2 className="text-5xl font-bold text-center mb-12 text-black tracking-widest uppercase font-serif italic">Cursos de IA más populares</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="bg-white rounded-3xl p-10 flex flex-col justify-between border-2 border-[#E3D6FF]" style={{ boxShadow: '0 2px 8px 0 #E3D6FF22' }}>
              <div>
                <h3 className="text-2xl font-semibold mb-4 text-black font-serif uppercase tracking-widest italic">Introducción a la IA</h3>
                <p className="mb-6 text-neutral-700 font-light">Aprende los conceptos básicos de la inteligencia artificial y sus aplicaciones.</p>
              </div>
              <a href="/cursos/intro-ia" className="text-[#A259FF] underline mt-auto font-bold uppercase tracking-widest">Ver curso</a>
            </div>
            <div className="bg-white rounded-3xl p-10 flex flex-col justify-between border-2 border-[#E3D6FF]" style={{ boxShadow: '0 2px 8px 0 #E3D6FF22' }}>
              <div>
                <h3 className="text-2xl font-semibold mb-4 text-black font-serif uppercase tracking-widest italic">IA para Negocios</h3>
                <p className="mb-6 text-neutral-700 font-light">Descubre cómo la IA puede transformar tu empresa y tus procesos.</p>
              </div>
              <a href="/cursos/ia-negocios" className="text-[#A259FF] underline mt-auto font-bold uppercase tracking-widest">Ver curso</a>
            </div>
            <div className="bg-white rounded-3xl p-10 flex flex-col justify-between border-2 border-[#E3D6FF]" style={{ boxShadow: '0 2px 8px 0 #E3D6FF22' }}>
              <div>
                <h3 className="text-2xl font-semibold mb-4 text-black font-serif uppercase tracking-widest italic">Prompt Engineering</h3>
                <p className="mb-6 text-neutral-700 font-light">Domina la creación de prompts efectivos para modelos de lenguaje.</p>
              </div>
              <a href="/cursos/prompt-engineering" className="text-[#A259FF] underline mt-auto font-bold uppercase tracking-widest">Ver curso</a>
            </div>
          </div>
        </section>

        {/* Logos de empresas y CTA demo (al final) */}
        <section className="w-full max-w-6xl mt-28 mb-20 flex flex-col items-center">
          <LogoMarquee />
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-8 text-black tracking-widest uppercase font-serif italic">
            Más de <span className="font-extrabold">3000</span> empresas usan IAcademy para la formación de sus equipos
          </h2>
          <a
            href="/demo"
            className="mt-4 px-12 py-5 border-2 border-black rounded-full font-bold uppercase tracking-widest bg-white text-black hover:bg-black hover:text-white transition text-xl" style={{boxShadow: '0 4px 24px 0 #FFD70022'}}>
            Agenda una demo
          </a>
        </section>

        {/* b Platform Section */}
        <section className="w-full max-w-6xl flex flex-col md:flex-row items-center justify-between gap-20 py-24 px-4">
          <div className="flex-1 mb-10 md:mb-0">
            <div className="flex items-center gap-4 mb-8">
              <svg width="36" height="36" fill="none" viewBox="0 0 24 24"><rect width="24" height="24" rx="6" fill="#FFD700"/><rect x="5" y="7" width="14" height="2" rx="1" fill="#23235F"/><rect x="5" y="11" width="14" height="2" rx="1" fill="#23235F"/><rect x="5" y="15" width="14" height="2" rx="1" fill="#23235F"/></svg>
              <span className="font-medium text-2xl text-black tracking-widest uppercase font-serif italic">The b Platform</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-extrabold leading-tight text-black tracking-widest uppercase font-serif italic">Made for Marketers Who Imagine More</h2>
          </div>
          <div className="flex-1 flex flex-col items-start">
            <p className="text-xl md:text-2xl mb-10 max-w-xl text-neutral-700 font-light">
              b isn't just another tool—it's your creative playground. Dream up bold campaigns, remix your brand's story, and automate the busywork. All your favorite creative powers, finally in one place.
            </p>
            <a href="#" className="px-12 py-5 rounded-3xl border-2 border-[#E3D6FF] bg-white text-black font-bold uppercase tracking-widest hover:bg-[#F3F7FF] hover:text-[#A259FF] transition text-xl">Explore the Platform</a>
          </div>
        </section>

        {/* b Features Cards Section */}
        <section className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 py-16 px-4">
          {/* Card 1 */}
          <div className="bg-white card flex flex-col justify-between min-h-[320px] transition relative border-2 border-[#E3D6FF] rounded-3xl" style={{ boxShadow: '0 2px 8px 0 #FFD70011' }}>
            <div>
              <div className="flex items-center justify-between mb-8">
                <span className="text-2xl font-bold text-black font-serif uppercase tracking-widest italic">b Studio</span>
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="3" stroke="#FFD700" strokeWidth="2"/><rect x="8" y="8" width="8" height="8" rx="2" stroke="#FFD700" strokeWidth="2"/></svg>
              </div>
              <p className="mb-8 text-neutral-700 font-light">Bring your wildest marketing ideas to life. b Studio lets you create, remix, and launch content with a touch of AI magic—no tech skills needed.</p>
            </div>
            <div className="flex justify-end">
              <span className="inline-block p-2 rounded-full hover:bg-[#FFD700]/10 transition">
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </span>
            </div>
          </div>
          {/* Card 2 */}
          <div className="bg-white card flex flex-col justify-between min-h-[320px] transition relative border-2 border-[#E3D6FF] rounded-3xl" style={{ boxShadow: '0 2px 8px 0 #FFD70011' }}>
            <div>
              <div className="flex items-center justify-between mb-8">
                <span className="text-2xl font-bold text-black font-serif uppercase tracking-widest italic">Marketing AI Toolkit</span>
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M12 3l2.09 6.26L21 9.27l-5 3.64L17.18 21 12 17.27 6.82 21 8 12.91l-5-3.64 6.91-1.01z" stroke="#FFD700" strokeWidth="2" strokeLinejoin="round"/></svg>
              </div>
              <p className="mb-8 text-neutral-700 font-light">Your creative Swiss Army knife: chat, write, design, edit, and organize—all powered by AI, all in one place. No more juggling apps or tabs.</p>
            </div>
            <div className="flex justify-end">
              <span className="inline-block p-2 rounded-full hover:bg-[#FFD700]/10 transition">
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </span>
            </div>
          </div>
          {/* Card 3 */}
          <div className="bg-white card flex flex-col justify-between min-h-[320px] transition relative border-2 border-[#E3D6FF] rounded-3xl" style={{ boxShadow: '0 2px 8px 0 #FFD70011' }}>
            <div>
              <div className="flex items-center justify-between mb-8">
                <span className="text-2xl font-bold text-black font-serif uppercase tracking-widest italic">Knowledge & Context</span>
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="3" stroke="#FFD700" strokeWidth="2"/><rect x="8" y="8" width="8" height="8" rx="2" stroke="#FFD700" strokeWidth="2"/></svg>
              </div>
              <p className="mb-8 text-neutral-700 font-light">b learns your brand's voice and context, so every output feels like you—only faster, and with a dash of AI brilliance.</p>
            </div>
            <div className="flex justify-end">
              <span className="inline-block p-2 rounded-full hover:bg-[#FFD700]/10 transition">
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </span>
            </div>
          </div>
          {/* Card 4 */}
          <div className="bg-white card flex flex-col justify-between min-h-[320px] transition relative border-2 border-[#E3D6FF] rounded-3xl" style={{ boxShadow: '0 2px 8px 0 #FFD70011' }}>
            <div>
              <div className="flex items-center justify-between mb-8">
                <span className="text-2xl font-bold text-black font-serif uppercase tracking-widest italic">Trust Foundation</span>
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M12 2l7 4v6c0 5.25-3.5 10-7 10s-7-4.75-7-10V6l7-4z" stroke="#FFD700" strokeWidth="2" strokeLinejoin="round"/></svg>
              </div>
              <p className="mb-8 text-neutral-700 font-light">Your ideas are safe here. b keeps your data private and secure, so you can create with confidence and focus on what matters—your next big idea.</p>
            </div>
            <div className="flex justify-end">
              <span className="inline-block p-2 rounded-full hover:bg-[#FFD700]/10 transition">
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </span>
            </div>
          </div>
        </section>

        {/* Customer Stories Section */}
        <section className="w-full max-w-7xl mx-auto py-16 px-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-12 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <svg width="22" height="22" fill="none" viewBox="0 0 24 24"><rect width="24" height="24" rx="6" fill="#FFD700"/><rect x="5" y="7" width="14" height="2" rx="1" fill="#23235F"/></svg>
                <span className="text-gray-500 font-medium text-lg">Customer Stories</span>
              </div>
              <h2 className="text-5xl font-extrabold text-gray-900 leading-tight mb-2">Real Marketers. Real Magic.</h2>
            </div>
            <div className="flex-1 flex flex-col items-start md:items-end justify-center">
              <p className="text-lg text-gray-700 mb-6 max-w-xl md:text-right">
                Join a growing community of marketers who are creating, launching, and winning with b's all-in-one creative AI.
              </p>
              <a href="#" className="px-8 py-3 border border-gray-800 rounded-lg font-semibold text-gray-900 hover:bg-gray-900 hover:text-white transition">See More Stories</a>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="bg-orange-50 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative">
              <div>
                <div className="text-5xl font-bold text-gray-900 mb-2">44</div>
                <div className="text-gray-700 mb-8">new articles published in record time [5/week]</div>
              </div>
              <div className="flex items-center justify-between">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6e/Goosehead_Insurance_logo.svg" alt="Goosehead Insurance" className="h-6" />
                <span className="inline-block p-2 rounded-full hover:bg-gray-100 transition">
                  <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </span>
              </div>
            </div>
            {/* Card 2 */}
            <div className="bg-blue-50 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative">
              <div>
                <div className="text-5xl font-bold text-gray-900 mb-2">10,000+</div>
                <div className="text-gray-700 mb-8">hours saved</div>
              </div>
              <div className="flex items-center justify-between">
                <img src="https://upload.wikimedia.org/wikipedia/commons/4/4a/Boeing_full_logo.svg" alt="Cushman & Wakefield" className="h-6" />
                <span className="inline-block p-2 rounded-full hover:bg-gray-100 transition">
                  <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </span>
              </div>
            </div>
            {/* Card 3 */}
            <div className="bg-gray-50 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative col-span-1 md:col-span-2 lg:col-span-1">
              <div className="flex items-center gap-4 mb-4">
                <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="Nick Kakanis" className="h-16 w-16 rounded-xl object-cover" />
                <div>
                  <div className="font-semibold text-gray-900">Nick Kakanis</div>
                  <div className="text-gray-500 text-sm">SVP of Operations</div>
                </div>
              </div>
              <div className="text-gray-700 mb-4">"b's brand and voice tools help our teams work even better together. We're able to align faster and collaborate more effectively."</div>
              <img src="https://upload.wikimedia.org/wikipedia/commons/2/2e/Pilot_Company_logo.svg" alt="Pilot Company" className="h-6" />
            </div>
            {/* Card 4 */}
            <div className="bg-gray-50 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative col-span-1 md:col-span-2 lg:col-span-1">
              <div className="flex items-center gap-4 mb-4">
                <img src="https://randomuser.me/api/portraits/women/44.jpg" alt="Dara Cohen" className="h-16 w-16 rounded-xl object-cover" />
                <div>
                  <div className="font-semibold text-gray-900">Dara Cohen</div>
                  <div className="text-gray-500 text-sm">Sr. Manager, Campaign Strategy</div>
                </div>
              </div>
              <div className="text-gray-700 mb-4">"We can be way more creative in what we're putting out into the world"</div>
              <img src="https://upload.wikimedia.org/wikipedia/commons/2/2b/CloudBees_logo.svg" alt="CloudBees" className="h-6" />
            </div>
            {/* Card 5 */}
            <div className="bg-purple-100 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative">
              <div>
                <div className="text-5xl font-bold text-gray-900 mb-2">3,000+</div>
                <div className="text-gray-700 mb-8">hours saved in content creation time</div>
              </div>
              <div className="flex items-center justify-between">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6e/WalkMe_logo.svg" alt="WalkMe" className="h-6" />
                <span className="inline-block p-2 rounded-full hover:bg-gray-100 transition">
                  <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </span>
              </div>
            </div>
            {/* Card 6 */}
            <div className="bg-orange-100 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative">
              <div>
                <div className="text-5xl font-bold text-gray-900 mb-2">800%</div>
                <div className="text-gray-700 mb-8">surge in web traffic</div>
              </div>
              <div className="flex items-center justify-between">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6e/Bestplaces_logo.svg" alt="Bestplaces" className="h-6" />
                <span className="inline-block p-2 rounded-full hover:bg-gray-100 transition">
                  <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </span>
              </div>
            </div>
            {/* Card 7 */}
            <div className="bg-blue-50 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative">
              <div>
                <div className="text-5xl font-bold text-gray-900 mb-2">40%</div>
                <div className="text-gray-700 mb-8">increase in traffic using b to produce better blog content</div>
              </div>
              <div className="flex items-center justify-between">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6e/Bloomreach_logo.svg" alt="Bloomreach" className="h-6" />
                <span className="inline-block p-2 rounded-full hover:bg-gray-100 transition">
                  <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </span>
              </div>
            </div>
            {/* Card 8 */}
            <div className="bg-green-100 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative">
              <div>
                <div className="text-5xl font-bold text-gray-900 mb-2">93%</div>
                <div className="text-gray-700 mb-8">faster creation of campaigns</div>
              </div>
              <div className="flex items-center justify-between">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6e/Commercetools_logo.svg" alt="Commercetools" className="h-6" />
                <span className="inline-block p-2 rounded-full hover:bg-gray-100 transition">
                  <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </span>
              </div>
            </div>
            {/* Card 9 */}
            <div className="bg-gray-50 rounded-2xl p-8 flex flex-col justify-between min-h-[180px] relative col-span-1 md:col-span-2 lg:col-span-1">
              <div className="flex items-center gap-4 mb-4">
                <img src="https://randomuser.me/api/portraits/men/45.jpg" alt="Mark Wollney" className="h-16 w-16 rounded-xl object-cover" />
                <div>
                  <div className="font-semibold text-gray-900">Mark Wollney</div>
                  <div className="text-gray-500 text-sm">SVP of Operations</div>
                </div>
              </div>
              <div className="text-gray-700 mb-4">"This isn't just about staying relevant in a rapidly evolving industry; it's about leading the way."</div>
              <img src="https://upload.wikimedia.org/wikipedia/commons/6/6e/Merge_logo.svg" alt="Merge" className="h-6" />
            </div>
          </div>
        </section>

        {/* AI Success Section */}
        <section className="w-full max-w-7xl mx-auto py-16 px-4">
          <h2 className="text-5xl font-extrabold text-gray-900 text-center mb-12">Start Your AI Journey</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Card 1 */}
            <div className="card flex flex-col items-center text-center shadow hover:shadow-lg transition bg-green-50">
              <svg width="96" height="96" fill="none" viewBox="0 0 96 96" className="mb-6"><rect x="8" y="8" width="80" height="80" rx="40" fill="#D1FAE5"/><path d="M48 64c8.837 0 16-7.163 16-16S56.837 32 48 32 32 39.163 32 48s7.163 16 16 16Z" stroke="#34D399" strokeWidth="3"/><path d="M48 56c4.418 0 8-3.582 8-8s-3.582-8-8-8-8 3.582-8 8 3.582 8 8 8Z" stroke="#34D399" strokeWidth="3"/><path d="M48 48v-8" stroke="#34D399" strokeWidth="3" strokeLinecap="round"/><path d="M48 48l5.657 5.657" stroke="#34D399" strokeWidth="3" strokeLinecap="round"/></svg>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Connect with Community</h3>
              <p className="text-gray-600 mb-6">Guides, courses, events, and a friendly community to help you grow as a marketer and creator.</p>
              <a href="#" className="font-semibold text-green-700 hover:underline flex items-center gap-1">Explore the Community <span>&rarr;</span></a>
            </div>
            {/* Card 2 */}
            <div className="card flex flex-col items-center text-center shadow hover:shadow-lg transition bg-blue-50">
              <svg width="96" height="96" fill="none" viewBox="0 0 96 96" className="mb-6"><rect x="8" y="8" width="80" height="80" rx="40" fill="#DBEAFE"/><path d="M32 64V48l16-8 16 8v16" stroke="#3B82F6" strokeWidth="3"/><path d="M32 64h32" stroke="#3B82F6" strokeWidth="3" strokeLinecap="round"/></svg>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Watch b Foundations</h3>
              <p className="text-gray-600 mb-6">Learn the basics and discover creative ways to use b for your next big project.</p>
              <a href="#" className="font-semibold text-blue-700 hover:underline flex items-center gap-1">Start watching <span>&rarr;</span></a>
            </div>
            {/* Card 3 */}
            <div className="card flex flex-col items-center text-center shadow hover:shadow-lg transition bg-purple-50">
              <svg width="96" height="96" fill="none" viewBox="0 0 96 96" className="mb-6"><rect x="8" y="8" width="80" height="80" rx="40" fill="#EDE9FE"/><path d="M48 64c8.837 0 16-7.163 16-16S56.837 32 48 32 32 39.163 32 48s7.163 16 16 16Z" stroke="#8B5CF6" strokeWidth="3"/><path d="M48 48v-8" stroke="#8B5CF6" strokeWidth="3" strokeLinecap="round"/><path d="M48 56h.01" stroke="#8B5CF6" strokeWidth="3" strokeLinecap="round"/><rect x="40" y="40" width="16" height="16" rx="8" stroke="#8B5CF6" strokeWidth="3"/></svg>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Search Knowledge Center</h3>
              <p className="text-gray-600 mb-6">Find tips, answers, and inspiration for using AI in your marketing role—no matter your experience level.</p>
              <a href="#" className="font-semibold text-purple-700 hover:underline flex items-center gap-1">Search Knowledge Center <span>&rarr;</span></a>
            </div>
          </div>
        </section>
      </main>
      {/* Footer tipo Cursor */}
      <footer className="w-full bg-gray-50 py-12 px-4 border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-5 gap-8 text-gray-700">
          <div className="flex flex-col gap-4">
            <a href="mailto:hi@iacademy.com" className="font-semibold hover:underline">hi@iacademy.com ↗</a>
            <div className="flex gap-3 text-xl">
              <a href="#"><span className="sr-only">X</span>✖️</a>
              <a href="#"><span className="sr-only">GitHub</span>🐙</a>
              <a href="#"><span className="sr-only">Reddit</span>👽</a>
              <a href="#"><span className="sr-only">YouTube</span>▶️</a>
            </div>
            <span className="text-xs mt-4">© {new Date().getFullYear()} Made by IAcademy</span>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Product</h4>
            <ul className="space-y-1">
              <li><a href="/pricing" className="hover:underline">Pricing</a></li>
              <li><a href="/features" className="hover:underline">Features</a></li>
              <li><a href="/enterprise" className="hover:underline">Enterprise</a></li>
              <li><a href="/downloads" className="hover:underline">Downloads</a></li>
              <li><a href="/students" className="hover:underline">Students</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Resources</h4>
            <ul className="space-y-1">
              <li><a href="/docs" className="hover:underline">Docs</a></li>
              <li><a href="/blog" className="hover:underline">Blog</a></li>
              <li><a href="/forum" className="hover:underline">Forum</a></li>
              <li><a href="/changelog" className="hover:underline">Changelog</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Company</h4>
            <ul className="space-y-1">
              <li><a href="/about" className="hover:underline">IAcademy</a></li>
              <li><a href="/careers" className="hover:underline">Careers</a></li>
              <li><a href="/community" className="hover:underline">Community</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Legal</h4>
            <ul className="space-y-1">
              <li><a href="/terms" className="hover:underline">Terms</a></li>
              <li><a href="/security" className="hover:underline">Security</a></li>
              <li><a href="/privacy" className="hover:underline">Privacy</a></li>
            </ul>
          </div>
        </div>
      </footer>
    </>
  );
} 