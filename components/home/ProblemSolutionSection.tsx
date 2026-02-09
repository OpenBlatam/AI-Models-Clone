export function ProblemSolutionSection() {
  return (
    <section className="w-full max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-20 py-24 px-4">
      {/* Left: Problem */}
      <div
        className="bg-white rounded-3xl p-14 flex flex-col items-center border-2 border-[#E3D6FF]"
        style={{ boxShadow: "0 2px 8px 0 #E3D6FF22" }}
      >
        <h2 className="text-5xl font-extrabold mb-8 text-black tracking-widest uppercase font-serif italic">
          AI for marketing is fragmented.
        </h2>
        <p className="text-xl mb-10 text-center text-neutral-700 font-light">
          Jumping between OpusClip, b, HeyGen, Blaze AI, and more? App-switching slows you down, breaks your flow,
          and makes creative work harder than it should be.
        </p>
        <div className="flex flex-wrap gap-8 justify-center">
          <img src="/logos/opusclip.png" alt="OpusClip" className="h-14 rounded-2xl bg-white p-4 border-2 border-[#E3D6FF]" />
          <img src="/logos/b.png" alt="b" className="h-14 rounded-2xl bg-white p-4 border-2 border-[#E3D6FF]" />
          <img src="/logos/heygen.png" alt="HeyGen" className="h-14 rounded-2xl bg-white p-4 border-2 border-[#E3D6FF]" />
          <img src="/logos/blazeai.png" alt="Blaze AI" className="h-14 rounded-2xl bg-white p-4 border-2 border-[#E3D6FF]" />
        </div>
      </div>

      {/* Right: Solution */}
      <div
        className="bg-white rounded-3xl p-14 flex flex-col items-center border-2 border-[#E3D6FF]"
        style={{ boxShadow: "0 2px 8px 0 #FFD70011" }}
      >
        <h2 className="text-5xl font-extrabold mb-8 text-black tracking-widest uppercase font-serif italic">
          Let&apos;s fix it.
        </h2>
        <p className="text-xl mb-10 text-center text-neutral-700 font-light">
          Meet the everything AI marketing platform. All your creative, content, and campaign tools—together in one
          magical workspace. No more switching. Just flow.
        </p>
        <a
          href="/trial"
          className="px-12 py-5 rounded-3xl font-extrabold text-2xl shadow-2xl transition-transform duration-200 hover:scale-105 border-0"
          style={{
            background: "linear-gradient(90deg, #FFD6E3 0%, #E3D6FF 100%)",
            color: "#23235F",
            boxShadow: "0 4px 24px 0 #FFD70022",
            letterSpacing: "0.02em",
          }}
        >
          Get started. It&apos;s FREE!
        </a>
        <p className="text-center font-medium mt-4 text-neutral-500 text-lg">Free Forever. No Credit Card.</p>
      </div>
    </section>
  );
}















