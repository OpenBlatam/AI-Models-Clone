"use client";

import { useState } from "react";
import Link from "next/link";
import { Music, X, Sparkles, Heart, Play as PlayIcon } from "lucide-react";
import "@/styles/globals.css";

export default function SunoHomePage() {
  const [prompt, setPrompt] = useState("");

  const popularSongs = [
    { title: "Liberty or Cruelty...? Dim Candles", likes: "2.1K", plays: "85K" },
    { title: "Play the Card BettyByte", likes: "465", plays: "6.8K" },
    { title: "Memory JoonOc", likes: "4.6K", plays: "142K" },
    { title: "Delapidated (Cover) DeeBeetttZZ", likes: "1.5K", plays: "82K" },
    { title: "Parental Burnout The Beat Bastard", likes: "733", plays: "30K" },
    { title: "take me with her Sol", likes: "256", plays: "12K" },
    { title: "Everything's Fine Staabworth", likes: "3.7K", plays: "108K" },
    { title: "Bittersweet Gravity Wistaria Addict", likes: "2.2K", plays: "72K" },
    { title: "Mojave HighSpeedOutro9488", likes: "757", plays: "35K" },
    { title: "April's Gone Thomas Otten", likes: "2.4K", plays: "88K" },
    { title: "Lo-Fi Rock Stray Cat/Game Dev", likes: "498", plays: "30K" },
    { title: "Something is going down XAVI", likes: "1.4K", plays: "58K" },
    { title: "Signal Fade MakMuzical", likes: "1.0K", plays: "52K" },
    { title: "Moth Among the Stars (Live) Sam", likes: "1.9K", plays: "79K" },
    { title: "passing by bleeder", likes: "638", plays: "17K" },
    { title: "change GTZY", likes: "713", plays: "27K" },
    { title: "almost home Making Music Is Life", likes: "1.4K", plays: "49K" },
    { title: "Muse onoa", likes: "191", plays: "14K" },
    { title: "lilies in the pond. a.astronaut", likes: "1.5K", plays: "33K" },
    { title: "I am in - I am out EDM EUMAK4U", likes: "960", plays: "38K" },
    { title: "Stuck In My Head Kotaboda", likes: "823", plays: "39K" },
  ];

  return (
    <div className="min-h-screen bg-white text-black">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2 text-2xl font-bold">
            SUNO
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="px-4 py-2 text-sm font-medium hover:text-gray-600 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 text-sm font-medium bg-black text-white rounded-full hover:bg-gray-800 transition-colors"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="py-16 px-4">
          <div className="container mx-auto max-w-4xl text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              Make any <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">song</span> you can imagine
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Start with a simple prompt or dive into our pro editing tool, your next track is just a step away.
            </p>

            {/* Chat Input */}
            <div className="relative max-w-2xl mx-auto">
              <div className="flex items-center border-2 border-gray-300 rounded-full px-4 py-3 bg-white shadow-sm hover:border-gray-400 transition-colors">
                <input
                  type="text"
                  placeholder="Chat to make music"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="flex-1 outline-none text-lg"
                />
                <div className="flex items-center gap-2">
                  {prompt && (
                    <button
                      onClick={() => setPrompt("")}
                      className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                    >
                      <X className="w-5 h-5 text-gray-500" />
                    </button>
                  )}
                  <button className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors">
                    Advanced
                  </button>
                  <button className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors flex items-center gap-1">
                    <Sparkles className="w-4 h-4" />
                    Generate random prompt
                  </button>
                  <button className="px-6 py-2 bg-black text-white rounded-full hover:bg-gray-800 transition-colors font-medium flex items-center gap-2">
                    <Music className="w-5 h-5" />
                    Create
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Popular Songs Grid */}
        <section className="py-16 px-4 bg-gray-50">
          <div className="container mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {popularSongs.map((song, index) => (
                <button
                  key={index}
                  className="group relative aspect-square bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all text-left p-4 flex flex-col justify-between"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-100 to-pink-100 opacity-0 group-hover:opacity-100 transition-opacity" />
                  <div className="relative z-10 flex-1 flex flex-col">
                    <div className="flex-1" />
                    <div className="mt-auto">
                      <p className="font-semibold text-sm mb-1 line-clamp-2">{song.title}</p>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <PlayIcon className="w-3 h-3" />
                          {song.plays}
                        </span>
                        <span className="flex items-center gap-1">
                          <Heart className="w-3 h-3" />
                          {song.likes}
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section className="py-16 px-4">
          <div className="container mx-auto max-w-6xl">
            <div className="flex justify-center gap-2 mb-8">
              <button className="px-4 py-2 bg-black text-white rounded-full text-sm font-medium">
                Monthly
              </button>
              <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm font-medium hover:bg-gray-200 transition-colors">
                Yearly <span className="text-green-600">save 20%</span>
              </button>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {/* Free Plan */}
              <div className="border-2 border-gray-200 rounded-2xl p-6">
                <h3 className="text-2xl font-bold mb-2">Free Plan</h3>
                <p className="text-gray-600 mb-6">Our starter plan.</p>
                <button className="w-full py-3 bg-black text-white rounded-full font-medium hover:bg-gray-800 transition-colors mb-6">
                  Sign Up
                </button>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Access to v4.5-all</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">50 credits renew daily (10 songs)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">No commercial use</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Standard features only</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Upload up to 1 min of audio</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Shared creation queue</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">No add-on credit purchase</span>
                  </li>
                </ul>
              </div>

              {/* Pro Plan */}
              <div className="border-2 border-black rounded-2xl p-6 relative">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-black text-white text-xs font-medium rounded-full">
                  POPULAR
                </div>
                <h3 className="text-2xl font-bold mb-2">Pro Plan</h3>
                <p className="text-gray-600 mb-6">Access to our best models and editing tools.</p>
                <button className="w-full py-3 bg-black text-white rounded-full font-medium hover:bg-gray-800 transition-colors mb-6">
                  Subscribe
                </button>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Access to latest and most advanced v5 model</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">2,500 credits (up to 500 songs), refreshes monthly</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Commercial use rights for new songs made</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Standard + Pro features (personal and advanced editing)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Split songs into up to 12 vocal and instrumental stems</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Upload up to 8 min of audio</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Add new vocals or instrumentals to existing songs</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Early access to new features</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Ability to purchase add-on credits</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Priority queue, up to 10 songs at once</span>
                  </li>
                </ul>
              </div>

              {/* Premier Plan */}
              <div className="border-2 border-gray-200 rounded-2xl p-6">
                <h3 className="text-2xl font-bold mb-2">Premier Plan</h3>
                <p className="text-gray-600 mb-6">Maximum credits and every feature unlocked.</p>
                <button className="w-full py-3 bg-black text-white rounded-full font-medium hover:bg-gray-800 transition-colors mb-6">
                  Subscribe
                </button>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Access to Suno Studio</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Access to latest and most advanced v5 model</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">10,000 credits (up to 2,000 songs), refreshes monthly</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Commercial use rights for new songs made</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Standard + Pro features (personal and advanced editing)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Split songs into up to 12 vocal and instrumental stems</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Upload up to 8 min of audio</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Add new vocals or instrumentals to existing songs</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Early access to new features</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Ability to purchase add-on credits</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span className="text-sm">Priority queue, up to 10 songs at once</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* App Download Section */}
        <section className="py-16 px-4 bg-black text-white">
          <div className="container mx-auto max-w-4xl text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">The #1 AI music app</h2>
            <p className="text-xl text-gray-300 mb-8">
              Where you can discover, create and share from anywhere because music has no boundaries.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-6 py-3 bg-white text-black rounded-full font-medium hover:bg-gray-100 transition-colors flex items-center justify-center gap-2">
                <span>Download on iPhone</span>
              </button>
              <button className="px-6 py-3 bg-white text-black rounded-full font-medium hover:bg-gray-100 transition-colors flex items-center justify-center gap-2">
                <span>Download on Android</span>
              </button>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 px-4 bg-gray-50">
          <div className="container mx-auto max-w-4xl text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Explore and get inspired</h2>
            <p className="text-xl text-gray-600 mb-8">
              Join the #1 AI music generator. Create songs, remix tracks, make beats, and share your music with millions — free forever.
            </p>
            <button className="px-8 py-4 bg-black text-white rounded-full font-medium text-lg hover:bg-gray-800 transition-colors">
              Sign up for free
            </button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="font-semibold mb-4">Brand</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="/about" className="hover:text-black transition-colors">About</Link></li>
                <li><Link href="/careers" className="hover:text-black transition-colors">Work at Suno</Link></li>
                <li><Link href="/blog" className="hover:text-black transition-colors">Blog</Link></li>
                <li><Link href="/pricing" className="hover:text-black transition-colors">Pricing</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="/help" className="hover:text-black transition-colors">Help</Link></li>
                <li><Link href="/contact" className="hover:text-black transition-colors">Contact Us</Link></li>
                <li><Link href="/faq" className="hover:text-black transition-colors">FAQ</Link></li>
                <li><Link href="/terms" className="hover:text-black transition-colors">Terms of Service</Link></li>
                <li><Link href="/privacy" className="hover:text-black transition-colors">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>
          <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t text-sm text-gray-600">
            <p>© 2025 Suno, Inc.</p>
            <div className="flex gap-4 mt-4 md:mt-0">
              <Link href="https://twitter.com" className="hover:text-black transition-colors">Twitter</Link>
              <Link href="https://instagram.com" className="hover:text-black transition-colors">Instagram</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
