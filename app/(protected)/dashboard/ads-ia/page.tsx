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
import { TemplateSelector } from "@/components/BrandKit/TemplateSelector";
import { AudienceModal } from "@/components/BrandKit/AudienceModal";
import type { BrandKitData } from "@/components/BrandKit/BrandKit";

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
    <div className="max-w-4xl mx-auto py-12 space-y-8">
      <h1 className="text-3xl font-bold mb-4">Herramientas de Marketing</h1>
      <p className="text-muted-foreground mb-6">
        Genera anuncios y brand kits automáticamente a partir de cualquier URL.
      </p>

      <div className="flex gap-2 mb-4">
        <input
          type="url"
          className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Pega aquí la URL de cualquier web..."
          value={url}
          onChange={e => setUrl(e.target.value)}
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="ads">Generar Anuncios</TabsTrigger>
          <TabsTrigger value="brand-kit">Generar Brand Kit</TabsTrigger>
        </TabsList>

        <TabsContent value="ads">
          <Card>
            <CardHeader>
              <CardTitle>Generador de Anuncios</CardTitle>
              <CardDescription>
                Genera anuncios optimizados para redes sociales a partir de cualquier web.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => handleExtract("ads")} 
                disabled={!url || loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generando anuncios...
                  </>
                ) : (
                  "Generar Anuncios"
                )}
              </Button>

              {error && (
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
              )}
              
              {ads.length > 0 && (
                <div className="mt-6 space-y-4">
                  <h2 className="text-xl font-semibold">Anuncios Generados:</h2>
                  <ul className="space-y-2">
                    {ads.map((ad, i) => (
                      <li key={i} className="bg-muted rounded-lg p-4 border border-border whitespace-pre-line">
                        {ad}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="brand-kit">
          <Card>
            <CardHeader>
              <CardTitle>Generador de Brand Kit</CardTitle>
              <CardDescription>
                Extrae y genera un brand kit completo a partir de cualquier web.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => handleExtract("brand-kit")} 
                disabled={!url || loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generando brand kit...
                  </>
                ) : (
                  "Generar Brand Kit"
                )}
              </Button>

              {error && (
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
              )}
              
              {brandKit && (
                <>
                  <div className="mt-6 space-y-4">
                    <h2 className="text-xl font-semibold">Brand Kit Generado:</h2>
                    <div className="bg-muted rounded-lg p-4 border border-border whitespace-pre-line">
                      {brandKit}
                    </div>
                  </div>
                  {brandKitData && (
                    <div className="mt-6 space-y-4">
                      <h2 className="text-xl font-semibold">Brand Kit Modular:</h2>
                      <BrandKitComponent data={brandKitData} />
                    </div>
                  )}
                  <BrandKitWizardModal
                    open={wizardOpen}
                    onClose={() => setWizardOpen(false)}
                    onGenerate={tpl => {
                      setSelectedTemplate(tpl);
                      setWizardOpen(false);
                    }}
                    brandKit={brandKit}
                  />
                </>
              )}
              <TemplateSelector
                onSelect={tpl => {
                  setSelectedTemplateForAudience(tpl);
                  setAudienceModalOpen(true);
                }}
              />
              <AudienceModal
                open={audienceModalOpen}
                onClose={() => {
                  setAudienceModalOpen(false);
                  setGeneratedContent("");
                }}
                onGenerate={handleGenerateContent}
                loading={audienceLoading}
                generatedContent={generatedContent}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 