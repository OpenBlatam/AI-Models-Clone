import { FEATURE_CARDS } from "@/app/home/constants";

export function FeatureCardsSection() {
  return (
    <section className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 py-16 px-4">
      {FEATURE_CARDS.map((card, index) => (
        <div
          key={index}
          className="bg-white card flex flex-col justify-between min-h-[320px] transition relative border-2 border-[#E3D6FF] rounded-3xl"
          style={{ boxShadow: "0 2px 8px 0 #FFD70011" }}
        >
          <div>
            <div className="flex items-center justify-between mb-8">
              <span className="text-2xl font-bold text-black font-serif uppercase tracking-widest italic">
                {card.title}
              </span>
              {card.icon}
            </div>
            <p className="mb-8 text-neutral-700 font-light">{card.description}</p>
          </div>
          <div className="flex justify-end">
            <span className="inline-block p-2 rounded-full hover:bg-[#FFD700]/10 transition">
              <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
                <path
                  d="M9 5l7 7-7 7"
                  stroke="#FFD700"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
          </div>
        </div>
      ))}
    </section>
  );
}















