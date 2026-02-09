import LogoMarquee from "@/components/LogoMarquee";

export function LogoMarqueeSection() {
  return (
    <section className="w-full max-w-6xl mt-28 mb-20 flex flex-col items-center">
      <LogoMarquee />
      <h2 className="text-4xl md:text-5xl font-bold text-center mb-8 text-black tracking-widest uppercase font-serif italic">
        Más de <span className="font-extrabold">3000</span> empresas usan IAcademy para la formación de sus equipos
      </h2>
      <a
        href="/demo"
        className="mt-4 px-12 py-5 border-2 border-black rounded-full font-bold uppercase tracking-widest bg-white text-black hover:bg-black hover:text-white transition text-xl"
        style={{ boxShadow: "0 4px 24px 0 #FFD70022" }}
      >
        Agenda una demo
      </a>
    </section>
  );
}















