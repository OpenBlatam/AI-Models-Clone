"use client";
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { BrandKitWizardModal } from "@/components/BrandKit/BrandKitWizardModal";
import { parseBrandKit } from "@/utils/parseBrandKit";
import { BrandKit as BrandKitComponent } from "@/components/BrandKit/BrandKit";
import { TemplateCarousel, templateCategories, TemplateDetailModal } from "@/components/BrandKit/TemplateSelector";
import { AudienceModal } from "@/components/BrandKit/AudienceModal";
import type { BrandKitData } from "@/components/BrandKit/BrandKit";
import { motion, AnimatePresence } from "framer-motion";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { Sparkles, Send, Wand2, Palette, Rocket, Crown, Star, Gem } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import BrandKitDisplay from "@/components/BrandKit/BrandKitDisplay";
import HeroSection from "@/components/ui/HeroSection";
import UrlInputBox from "@/components/ui/UrlInputBox";

function mapBrandKitDataToDisplay(data) {
  return {
    brand: {
      name: "Brand Name",
      logo: "/logo-placeholder.png",
    },
    voice: {
      purpose: data.fonts?.title || "",
      audience: data.fonts?.subtitle || "",
      tone: [],
      emotions: [],
    },
    materials: [],
    media: [],
  };
}

export default function AdsIaPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [ads, setAds] = useState<string[]>([]);
  const [brandKit, setBrandKit] = useState("");
  const [error, setError] = useState<{ message: string; details?: string } | null>(null);
  const [activeTab, setActiveTab] = useState("ads");
  const [wizardOpen, setWizardOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [brandKitData, setBrandKitData] = useState<BrandKitData | null>(null);
  const [selectedTemplateForAudience, setSelectedTemplateForAudience] = useState<{ id: number; title: string; color: string; image: string } | null>(null);
  const [audienceModalOpen, setAudienceModalOpen] = useState(false);
  const [audienceLoading, setAudienceLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState("");
  const [selectedTemplateDetail, setSelectedTemplateDetail] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);

  const handleExtract = async (type: "ads" | "brand-kit") => {
    setLoading(true);
    setError(null);
    setAds([]);
    setBrandKit("");
    
    try {
      const res = await fetch("/api/ads-ia", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, type }),
      });
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.error || "Error al procesar la solicitud");
      }
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      if (type === "ads") {
        setAds(data.ads || []);
      } else {
        setBrandKit(data.brandKit || "");
        setWizardOpen(true);
      }
    } catch (e: any) {
      setError({
        message: e.message || "Error al procesar la solicitud",
        details: e.details || e.message
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (brandKit) {
      setBrandKitData(parseBrandKit(brandKit));
    }
  }, [brandKit]);

  const handleGenerateContent = async (audience: string) => {
    setAudienceLoading(true);
    setGeneratedContent("");
    try {
      const prompt = `Genera un post para ${audience} usando el template "${selectedTemplateForAudience?.title}".`;
      const res = await fetch("/api/ads-ia", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, type: "ads", prompt }),
      });
      const data = await res.json();
      setGeneratedContent(data.ads?.join("\n\n") || "No se pudo generar contenido.");
    } catch (e) {
      setGeneratedContent("Error al generar contenido.");
    } finally {
      setAudienceLoading(false);
    }
  };

  return (
    <>
      <HeroSection
        title={
          <span>
            Herramientas de{" "}
            <motion.span
              className="bg-gradient-to-r from-[#7b61ff] via-[#fbbf24] to-[#22c55e] bg-clip-text text-transparent font-extrabold tracking-tight drop-shadow-lg"
              initial={{ backgroundPosition: "0% 50%" }}
              animate={{ backgroundPosition: "100% 50%" }}
              transition={{
                repeat: Infinity,
                repeatType: "reverse",
                duration: 4,
                ease: "linear"
              }}
              style={{
                backgroundSize: "200% 200%",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent"
              }}
            >
              Marketing
            </motion.span>
          </span>
        }
        subtitle="Genera anuncios y brand kits automáticamente a partir de cualquier URL."
        backgroundClass="bg-black"
        textClass="text-white"
        linearGradientBackground={true}
        multicolorBackground={false}
      >
        <UrlInputBox
          value={url}
          onChange={setUrl}
          loading={loading}
          onGenerate={() => handleExtract(activeTab as "ads" | "brand-kit")}
          onTryExample={() => setUrl("https://ejemplo.com")}
          onUseText={() => setUrl("Ejemplo de texto para anuncio")}
          extraClass=""
        />
      </HeroSection>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-5xl mx-auto py-12 space-y-8 px-4 relative"
      >
        {/* Decorative elements */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.1 }}
          transition={{ delay: 1 }}
          className="absolute inset-0 pointer-events-none"
        >
          <div className="absolute top-0 left-1/4 w-64 h-64 bg-primary/20 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-primary/20 rounded-full blur-3xl" />
        </motion.div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 p-1 bg-muted/50 rounded-xl backdrop-blur-sm border border-border/50">
            <TabsTrigger 
              value="ads"
              className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm transition-all duration-200 flex items-center gap-2"
            >
              <Rocket className="w-4 h-4" />
              Generar Anuncios
            </TabsTrigger>
            <TabsTrigger 
              value="brand-kit"
              className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm transition-all duration-200 flex items-center gap-2"
            >
              <Palette className="w-4 h-4" />
              Generar Brand Kit
            </TabsTrigger>
          </TabsList>

          <TabsContent value="ads">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card className="border-2 hover:border-primary/50 transition-all duration-200 bg-background/50 backdrop-blur-sm shadow-xl shadow-primary/5">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Rocket className="w-6 h-6 text-primary" />
                    Generador de Anuncios
                  </CardTitle>
                  <CardDescription className="text-lg">
                    Genera anuncios optimizados para redes sociales a partir de cualquier web.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <Alert variant="destructive" className="mt-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Error</AlertTitle>
                        <AlertDescription>
                          {error.message}
                          {error.details && error.details !== error.message && (
                            <p className="mt-2 text-sm opacity-80">{error.details}</p>
                          )}
                        </AlertDescription>
                      </Alert>
                    </motion.div>
                  )}
                  
                  {ads.length > 0 && (
                    <motion.div 
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-6 space-y-4"
                    >
                      <h2 className="text-xl font-semibold flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-primary" />
                        Anuncios Generados:
                      </h2>
                      <ul className="space-y-3">
                        {ads.map((ad, i) => (
                          <motion.li 
                            key={i}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="bg-muted/50 backdrop-blur-sm rounded-xl p-4 border border-border hover:border-primary/50 transition-all duration-200 group shadow-lg shadow-primary/5"
                          >
                            <div className="flex items-start gap-3">
                              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1 ring-2 ring-primary/20">
                                <span className="text-primary font-medium">{i + 1}</span>
                              </div>
                              <p className="text-base leading-relaxed">{ad}</p>
                            </div>
                          </motion.li>
                        ))}
                      </ul>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="brand-kit">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card className="border-2 hover:border-primary/50 transition-all duration-200 bg-background/50 backdrop-blur-sm shadow-xl shadow-primary/5">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Palette className="w-6 h-6 text-primary" />
                    Generador de Brand Kit
                  </CardTitle>
                  <CardDescription className="text-lg">
                    Extrae y genera un brand kit completo a partir de cualquier web.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <Alert variant="destructive" className="mt-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Error</AlertTitle>
                        <AlertDescription>
                          {error.message}
                          {error.details && error.details !== error.message && (
                            <p className="mt-2 text-sm opacity-80">{error.details}</p>
                          )}
                        </AlertDescription>
                      </Alert>
                    </motion.div>
                  )}
                  
                  {brandKit && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-6"
                    >
                      <div className="mt-6 space-y-4">
                        <h2 className="text-xl font-semibold flex items-center gap-2">
                          <Sparkles className="w-5 h-5 text-primary" />
                          Brand Kit Generado:
                        </h2>
                        <div className="bg-muted/50 backdrop-blur-sm rounded-xl p-4 border border-border hover:border-primary/50 transition-all duration-200 shadow-lg shadow-primary/5">
                          {brandKit}
                        </div>
                      </div>
                      {brandKitData && (
                        <div className="mt-10">
                          <BrandKitDisplay
                            {...mapBrandKitDataToDisplay(brandKitData)}
                            onCreate={() => {}}
                          />
                        </div>
                      )}
                    </motion.div>
                  )}
                  <div className="space-y-12 mt-8">
                    {templateCategories.map(cat => (
                      <TemplateCarousel
                        key={cat.title}
                        title={cat.title}
                        templates={cat.templates}
                        onCardClick={tpl => {
                          setSelectedTemplateDetail(tpl);
                          setDetailModalOpen(true);
                        }}
                      />
                    ))}
                  </div>
                  <AudienceModal
                    open={audienceModalOpen}
                    onClose={() => {
                      setAudienceModalOpen(false);
                      setGeneratedContent("");
                    }}
                    onRegenerate={() => handleGenerateContent("")}
                    onNext={(audience, brandKitId, language) => {
                      handleGenerateContent(audience);
                    }}
                    suggestion={selectedTemplateForAudience?.title || ""}
                    loading={audienceLoading}
                    brandKitId={1}
                    language="es"
                  />
                  <TemplateDetailModal
                    open={detailModalOpen}
                    onClose={() => setDetailModalOpen(false)}
                    template={selectedTemplateDetail}
                    onUseTemplate={tpl => {
                      setSelectedTemplateForAudience(tpl);
                      setAudienceModalOpen(true);
                    }}
                  />
                  <BrandKitWizardModal
                    open={wizardOpen}
                    onClose={() => setWizardOpen(false)}
                    onGenerate={tpl => {
                      setSelectedTemplate(tpl);
                      setWizardOpen(false);
                    }}
                    brandKit={brandKit}
                  />
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </>
  );
} 