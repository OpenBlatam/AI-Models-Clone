export function HomeFooter() {
  return (
    <footer className="w-full bg-gray-50 py-12 px-4 border-t border-gray-200 mt-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-5 gap-8 text-gray-700">
        <div className="flex flex-col gap-4">
          <a href="mailto:hi@iacademy.com" className="font-semibold hover:underline">
            hi@iacademy.com ↗
          </a>
          <div className="flex gap-3 text-xl">
            <a href="#">
              <span className="sr-only">X</span>✖️
            </a>
            <a href="#">
              <span className="sr-only">GitHub</span>🐙
            </a>
            <a href="#">
              <span className="sr-only">Reddit</span>👽
            </a>
            <a href="#">
              <span className="sr-only">YouTube</span>▶️
            </a>
          </div>
          <span className="text-xs mt-4">© {new Date().getFullYear()} Made by IAcademy</span>
        </div>
        <div>
          <h4 className="font-semibold mb-2">Product</h4>
          <ul className="space-y-1">
            <li>
              <a href="/pricing" className="hover:underline">
                Pricing
              </a>
            </li>
            <li>
              <a href="/features" className="hover:underline">
                Features
              </a>
            </li>
            <li>
              <a href="/enterprise" className="hover:underline">
                Enterprise
              </a>
            </li>
            <li>
              <a href="/downloads" className="hover:underline">
                Downloads
              </a>
            </li>
            <li>
              <a href="/students" className="hover:underline">
                Students
              </a>
            </li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-2">Resources</h4>
          <ul className="space-y-1">
            <li>
              <a href="/docs" className="hover:underline">
                Docs
              </a>
            </li>
            <li>
              <a href="/blog" className="hover:underline">
                Blog
              </a>
            </li>
            <li>
              <a href="/forum" className="hover:underline">
                Forum
              </a>
            </li>
            <li>
              <a href="/changelog" className="hover:underline">
                Changelog
              </a>
            </li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-2">Company</h4>
          <ul className="space-y-1">
            <li>
              <a href="/about" className="hover:underline">
                IAcademy
              </a>
            </li>
            <li>
              <a href="/careers" className="hover:underline">
                Careers
              </a>
            </li>
            <li>
              <a href="/community" className="hover:underline">
                Community
              </a>
            </li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-2">Legal</h4>
          <ul className="space-y-1">
            <li>
              <a href="/terms" className="hover:underline">
                Terms
              </a>
            </li>
            <li>
              <a href="/security" className="hover:underline">
                Security
              </a>
            </li>
            <li>
              <a href="/privacy" className="hover:underline">
                Privacy
              </a>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
}















