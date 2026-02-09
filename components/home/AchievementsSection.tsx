import { ACHIEVEMENTS } from "@/app/home/constants";

export function AchievementsSection() {
  return (
    <section
      className="w-full bg-white py-24 px-8 text-center my-24 rounded-3xl border-2 border-[#E3D6FF]"
      style={{ boxShadow: "0 2px 8px 0 #FFD70011" }}
    >
      <h2 className="text-7xl font-serif italic font-extrabold mb-16 tracking-tight text-black">
        Nuestros Logros
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-6xl mx-auto">
        {ACHIEVEMENTS.map((achievement, index) => (
          <div key={index} className="flex flex-col items-center">
            <div className="w-20 h-20 rounded-full bg-[#F3F7FF] flex items-center justify-center mb-6">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#FFD700" strokeWidth="2">
                <path d={achievement.icon} />
              </svg>
            </div>
            <h3 className="text-3xl font-bold mb-4 text-black">{achievement.value}</h3>
            <p className="text-xl text-neutral-700 font-light">{achievement.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}















