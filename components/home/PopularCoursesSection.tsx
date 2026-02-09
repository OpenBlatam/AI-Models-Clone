import { POPULAR_COURSES } from "@/app/home/constants";

export function PopularCoursesSection() {
  return (
    <section className="mt-20 w-full max-w-5xl">
      <h2 className="text-5xl font-bold text-center mb-12 text-black tracking-widest uppercase font-serif italic">
        Cursos de IA más populares
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
        {POPULAR_COURSES.map((course) => (
          <div
            key={course.href}
            className="bg-white rounded-3xl p-10 flex flex-col justify-between border-2 border-[#E3D6FF]"
            style={{ boxShadow: "0 2px 8px 0 #E3D6FF22" }}
          >
            <div>
              <h3 className="text-2xl font-semibold mb-4 text-black font-serif uppercase tracking-widest italic">
                {course.title}
              </h3>
              <p className="mb-6 text-neutral-700 font-light">{course.description}</p>
            </div>
            <a
              href={course.href}
              className="text-[#A259FF] underline mt-auto font-bold uppercase tracking-widest"
            >
              Ver curso
            </a>
          </div>
        ))}
      </div>
    </section>
  );
}















