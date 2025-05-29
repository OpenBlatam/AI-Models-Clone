"use client";

import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { SearchFilter } from "@/components/academy/search-filter";
import { AcademyGrid } from "@/components/academy/academy-grid";
import { Academy } from "@/lib/types/academy";
import { useDebounce } from "@/hooks/use-debounce";
import { useToast } from "@/hooks/use-toast";
import { Metadata } from "next";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

const CATEGORIES = [
  "Desarrollo Web",
  "Diseño UI/UX",
  "Marketing Digital",
  "Data Science",
  "Programación",
  "Negocios",
];

const LEVELS = ["Principiante", "Intermedio", "Avanzado"];

export const metadata: Metadata = {
  title: "Academias | Blatam Academy",
  description: "Explora nuestras academias y comienza tu viaje de aprendizaje.",
};

export default function AcademyPage() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedLevel, setSelectedLevel] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [page, setPage] = useState(1);

  const debouncedSearch = useDebounce(searchQuery, 300);

  const {
    data: academiesData,
    isLoading,
    isError,
    fetchNextPage,
    hasNextPage,
  } = useQuery({
    queryKey: ["academies", debouncedSearch, selectedCategory, selectedLevel, page],
    queryFn: async () => {
      try {
        const response = await fetch(
          `/api/academies?search=${debouncedSearch}&category=${selectedCategory}&level=${selectedLevel}&page=${page}`
        );
        if (!response.ok) throw new Error("Error al cargar las academias");
        return response.json();
      } catch (error) {
        toast({
          title: "Error",
          description: "No se pudieron cargar las academias",
          variant: "destructive",
        });
        throw error;
      }
    },
  });

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    setPage(1);
  }, []);

  const handleCategoryChange = useCallback((category: string) => {
    setSelectedCategory(category);
    setPage(1);
  }, []);

  const handleLevelChange = useCallback((level: string) => {
    setSelectedLevel(level);
    setPage(1);
  }, []);

  const handleViewModeChange = useCallback((mode: "grid" | "list") => {
    setViewMode(mode);
  }, []);

  const handleLoadMore = useCallback(async () => {
    if (hasNextPage) {
      setPage((prev) => prev + 1);
      await fetchNextPage();
    }
  }, [hasNextPage, fetchNextPage]);

  const allAcademies = academiesData?.pages.flatMap((page: any) => page.academies) ?? [];

  return (
    <div className="container py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">Academias</h1>
          <p className="text-xl text-muted-foreground">
            Explora nuestras academias y comienza tu viaje de aprendizaje.
          </p>
        </div>
        <Button asChild variant="outline" className="gap-2">
          <Link href="/dashboard">
            <ArrowLeft className="w-4 h-4" />
            Regresar a los cursos
          </Link>
        </Button>
      </div>

      <SearchFilter
        onSearch={handleSearch}
        onCategoryChange={handleCategoryChange}
        onLevelChange={handleLevelChange}
        onViewModeChange={handleViewModeChange}
        categories={CATEGORIES}
        levels={LEVELS}
      />

      {isError ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">
            Ocurrió un error al cargar las academias
          </p>
        </div>
      ) : (
        <AcademyGrid
          academies={allAcademies}
          onLoadMore={handleLoadMore}
          hasMore={hasNextPage ?? false}
          isLoading={isLoading}
          viewMode={viewMode}
        />
      )}
    </div>
  );
} 