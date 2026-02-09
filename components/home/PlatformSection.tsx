export function PlatformSection() {
  return (
    <section className="w-full max-w-6xl flex flex-col md:flex-row items-center justify-between gap-20 py-24 px-4">
      <div className="flex-1 mb-10 md:mb-0">
        <div className="flex items-center gap-4 mb-8">
          <svg width="36" height="36" fill="none" viewBox="0 0 24 24">
            <rect width="24" height="24" rx="6" fill="#FFD700" />
            <rect x="5" y="7" width="14" height="2" rx="1" fill="#23235F" />
            <rect x="5" y="11" width="14" height="2" rx="1" fill="#23235F" />
            <rect x="5" y="15" width="14" height="2" rx="1" fill="#23235F" />
          </svg>
          <span className="font-medium text-2xl text-black tracking-widest uppercase font-serif italic">
            The b Platform
          </span>
        </div>
        <h2 className="text-5xl md:text-6xl font-extrabold leading-tight text-black tracking-widest uppercase font-serif italic">
          Made for Marketers Who Imagine More
        </h2>
      </div>
      <div className="flex-1 flex flex-col items-start">
        <p className="text-xl md:text-2xl mb-10 max-w-xl text-neutral-700 font-light">
          b isn&apos;t just another tool—it&apos;s your creative playground. Dream up bold campaigns, remix your
          brand&apos;s story, and automate the busywork. All your favorite creative powers, finally in one place.
        </p>
        <a
          href="#"
          className="px-12 py-5 rounded-3xl border-2 border-[#E3D6FF] bg-white text-black font-bold uppercase tracking-widest hover:bg-[#F3F7FF] hover:text-[#A259FF] transition text-xl"
        >
          Explore the Platform
        </a>
      </div>
    </section>
  );
}















