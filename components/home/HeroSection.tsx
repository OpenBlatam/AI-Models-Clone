export function HeroSection() {
  return (
    <div className="flex flex-col items-center justify-center py-32 w-full">
      {/* Da Vinci spiral icon */}
      <div className="mb-6">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <path
            d="M24 24c0-8 8-8 8 0s-8 8-8 0zm0 0c0-12 12-12 12 0s-12 12-12 0zm0 0c0-16 16-16 16 0s-16 16-16 0z"
            stroke="#FFD700"
            strokeWidth="2"
            fill="none"
          />
        </svg>
      </div>
      <span
        className="inline-block px-6 py-2 rounded-full border-2"
        style={{
          borderColor: "#E3D6FF",
          background: "#fff",
          color: "#A259FF",
          fontWeight: 700,
          fontSize: "1.1rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          marginBottom: "2rem",
          fontStyle: "italic",
        }}
      >
        The Everything App for Marketers
      </span>
      <h1 className="text-5xl md:text-6xl font-serif font-extrabold italic text-black tracking-tight leading-tight uppercase mb-8 animate-fadein">
        The Everything AI Marketing,<br />
        <span
          style={{
            background: "linear-gradient(90deg, #FFD6E3 0%, #E3D6FF 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            display: "inline-block",
          }}
        >
          for teams that create
        </span>
      </h1>
      <p className="text-2xl text-center text-neutral-700 mb-12 max-w-3xl font-light">
        All your marketing, content, and creative work—brainstormed, designed, written, and launched in one place.
        For every team, every campaign, every idea. All powered by AI.
      </p>
      <div className="flex flex-col sm:flex-row gap-6 justify-center w-full max-w-lg">
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
          Try b Free
        </a>
        <a
          href="/demo"
          className="px-12 py-5 rounded-3xl font-extrabold text-2xl border-2 border-black bg-white text-black hover:bg-black hover:text-white transition"
        >
          See It in Action
        </a>
      </div>
    </div>
  );
}















