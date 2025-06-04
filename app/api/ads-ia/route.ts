import { NextRequest, NextResponse } from "next/server";
import { openai } from "@/lib/openai";
import axios from "axios";
import * as cheerio from "cheerio";

export const runtime = "edge";

// Validate OpenAI configuration
if (!process.env.OPENAI_API_KEY) {
}

const DUMMY_BRAND_KIT = `1. PALETA DE COLORES:
- #FAF3F3, #FF6FA5, #FFD6E0, #B2F0F0, #F39AC1

2. TIPOGRAFÍA:
- Montserrat, Roboto, Inter

3. TONO DE VOZ:
- Innovador, Cercano, Inspirador

4. VALORES DE MARCA:
- Creatividad, Tecnología, Educación

5. ELEMENTOS VISUALES:
- Imágenes limpias, iconos modernos, estilo minimalista`;

export async function POST(req: NextRequest) {
  try {
    // Check OpenAI configuration
    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { 
          error: "Error de configuración",
          details: "La API key de OpenAI no está configurada"
        },
        { status: 500 }
      );
    }

    const { url, type = "ads" } = await req.json();
    if (!url) {
      return NextResponse.json({ error: "URL requerida" }, { status: 400 });
    }

    // Validate URL format
    try {
      new URL(url);
    } catch (e) {
      return NextResponse.json({ error: "URL inválida" }, { status: 400 });
    }

    // 1. Scraping con axios y cheerio
    let extracted = "";
    let brandElements = {
      colors: [] as string[],
      fonts: [] as string[],
      logos: [] as string[],
      taglines: [] as string[],
    };
    let scrapingOk = false;

    try {
      const { data } = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        timeout: 10000 // 10 second timeout
      });
      const $ = cheerio.load(data);
      
      // Extract brand elements
      $('style, [style]').each((_, el) => {
        const style = $(el).attr('style') || $(el).text();
        // Extract colors
        const colorMatches = style.match(/#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)/g) || [];
        brandElements.colors.push(...colorMatches);
        
        // Extract fonts
        const fontMatches = style.match(/font-family:\s*([^;]+)/g) || [];
        brandElements.fonts.push(...fontMatches.map(f => f.replace('font-family:', '').trim()));
      });

      // Extract logos
      $('img[src*="logo"], img[alt*="logo"]').each((_, el) => {
        const src = $(el).attr('src');
        if (src) brandElements.logos.push(src);
      });

      // Extract taglines
      $('h1, h2, .tagline, .slogan').each((_, el) => {
        const text = $(el).text().trim();
        if (text) brandElements.taglines.push(text);
      });

      const title = $('title').text().trim();
      const description = $('meta[name="description"]').attr('content')?.trim() || '';
      const h1 = $('h1').first().text().trim();
      const h2 = $('h2').first().text().trim();
      const mainContent = $('main, article, .content, #content').first().text().trim().slice(0, 500);
      
      extracted = [title, description, h1, h2, mainContent]
        .filter(Boolean)
        .join(' | ');



      scrapingOk = !!extracted && extracted.length > 10;

    } catch (scrapeError) {
      console.error('Error scraping URL:', scrapeError);
      // No return, fallback to generic prompt
    }

    if (type === "brand-kit") {
      let prompt = "";
      if (scrapingOk) {
        prompt = `Analiza el siguiente contenido de una web y genera un brand kit completo y detallado. El brand kit debe incluir:\n\n1. PALETA DE COLORES:\n- Colores principales encontrados: ${brandElements.colors.join(', ')}\n- Sugiere una paleta complementaria de 5 colores\n- Incluye códigos hexadecimales\n\n2. TIPOGRAFÍA:\n- Fuentes encontradas: ${brandElements.fonts.join(', ')}\n- Sugiere una combinación de fuentes para títulos y texto\n- Incluye fuentes de Google Fonts o similares\n\n3. TONO DE VOZ:\n- Analiza el contenido y describe el tono de comunicación\n- Sugiere 3-5 adjetivos que definan la personalidad de la marca\n- Incluye ejemplos de cómo comunicar\n\n4. VALORES DE MARCA:\n- Extrae los valores principales del contenido\n- Sugiere 3-5 valores clave\n- Incluye una breve descripción de cada valor\n\n5. ELEMENTOS VISUALES:\n- Sugiere estilos de imágenes e iconos\n- Recomienda un estilo de fotografía\n- Incluye guías para el uso de elementos visuales\n\nContenido extraído:\n${extracted}\n\nTaglines encontrados: ${brandElements.taglines.join(', ')}\n\nPor favor, estructura tu respuesta en estas 5 secciones, siendo específico y práctico en tus recomendaciones.`;
      } else {
        prompt = `No se pudo extraer contenido de la web (${url}). Genera un brand kit genérico para una marca tecnológica moderna.`;
      }
      try {
        const completion = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          messages: [
            { role: "system", content: "Eres un experto en branding y diseño de identidad visual. Tu tarea es analizar el contenido de una web y generar un brand kit completo y detallado. Sé específico, práctico y estructurado en tus recomendaciones." },
            { role: "user", content: prompt },
          ],
          max_tokens: 1500,
          temperature: 0.7,
        });

        const brandKit = completion.choices[0]?.message?.content || "";
        
        if (!brandKit || brandKit.length < 30) {
          // fallback dummy
          return NextResponse.json({ brandKit: DUMMY_BRAND_KIT, fallback: true });
        }

        return NextResponse.json({ brandKit });
      } catch (openaiError: any) {
        console.error('Error con OpenAI:', openaiError);
        return NextResponse.json({ brandKit: DUMMY_BRAND_KIT, fallback: true, error: "OpenAI error", details: openaiError.message }, { status: 200 });
      }
    } else {
      // Original ads generation logic
      const prompt = `Eres un experto en marketing digital. A partir del siguiente contenido extraído de una web, genera 3 anuncios atractivos para redes sociales (Facebook, Instagram, Google Ads). Los anuncios deben ser concisos, persuasivos y adaptados a cada plataforma. Devuelve solo los textos de los anuncios, separados por saltos de línea.\n\nContenido extraído:\n${extracted}`;

      try {
        const completion = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          messages: [
            { 
              role: "system", 
              content: "Eres un experto en marketing digital y copywriting. Tu tarea es crear anuncios persuasivos y efectivos para redes sociales." 
            },
            { role: "user", content: prompt },
          ],
          max_tokens: 400,
          temperature: 0.8,
        });

        const adsRaw = completion.choices[0]?.message?.content || "";
        
        if (!adsRaw) {
          throw new Error("No se pudo generar ningún anuncio");
        }

        const ads = adsRaw.split(/\n+/).filter(Boolean);

        if (!ads.length) {
          throw new Error("No se pudieron generar anuncios válidos");
        }

        return NextResponse.json({ ads });
      } catch (openaiError: any) {
        
        return NextResponse.json(
          { 
            error: "Error al generar los anuncios",
            details: openaiError.message || "Error desconocido"
          },
          { status: 500 }
        );
      }
    }
  } catch (e: any) {
    console.error('Error general:', e);
    console.error('Error stack:', e.stack);
    return NextResponse.json({ brandKit: DUMMY_BRAND_KIT, fallback: true, error: "Error general", details: e.message }, { status: 200 });
  }
}  