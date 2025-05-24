"use client"

import { useState, useRef, useEffect } from "react"
import { Stage, Layer, Image, Group } from "react-konva"
import useImage from "use-image"

interface ProductBuilderProps {
  initialCategory?: string
}

const GAME_CONFIGS = {
  bebida: {
    title: "Constructor de Bebidas",
    colors: ["#FF5733", "#33FF57", "#3357FF", "#F3FF33"],
    sizes: ["small", "medium", "large"],
    extras: ["Hielo", "Crema", "Chocolate", "Caramelo"],
    baseImage: "/images/products/base-cup.svg",
    lidImage: "/images/products/lid.svg",
    strawImage: "/images/products/straw.svg"
  },
  oficina: {
    title: "Constructor de Oficina",
    colors: ["#8B4513", "#2F4F4F", "#4B0082", "#800000"],
    sizes: ["compacto", "estándar", "espacioso"],
    extras: ["Plantas", "Lámparas", "Decoración", "Almacenamiento"],
    baseImage: "/images/products/desk.svg",
    lidImage: "/images/products/chair.svg",
    strawImage: "/images/products/accessories.svg"
  },
  ropa: {
    title: "Constructor de Ropa",
    colors: ["#000000", "#FFFFFF", "#FF0000", "#0000FF"],
    sizes: ["XS", "S", "M", "L", "XL"],
    extras: ["Accesorios", "Estampados", "Bolsillos", "Detalles"],
    baseImage: "/images/products/shirt.svg",
    lidImage: "/images/products/pants.svg",
    strawImage: "/images/products/accessories.svg"
  },
  avatar: {
    title: "Constructor de Avatar",
    colors: ["#FFD700", "#C0C0C0", "#CD7F32", "#000000"],
    sizes: ["pequeño", "mediano", "grande"],
    extras: ["Sombreros", "Gafas", "Accesorios", "Expresiones"],
    baseImage: "/images/products/face.svg",
    lidImage: "/images/products/hair.svg",
    strawImage: "/images/products/accessories.svg"
  }
}

export function ProductBuilder({ initialCategory = "bebida" }: ProductBuilderProps) {
  const [selectedCategory, setSelectedCategory] = useState(initialCategory)
  const [customizations, setCustomizations] = useState({
    color: GAME_CONFIGS[initialCategory as keyof typeof GAME_CONFIGS].colors[0],
    size: GAME_CONFIGS[initialCategory as keyof typeof GAME_CONFIGS].sizes[0],
    extras: [] as string[],
  })
  
  const stageRef = useRef(null)
  const config = GAME_CONFIGS[selectedCategory as keyof typeof GAME_CONFIGS]
  const [baseImage] = useImage(config.baseImage)
  const [lidImage] = useImage(config.lidImage)
  const [strawImage] = useImage(config.strawImage)

  useEffect(() => {
    setSelectedCategory(initialCategory)
    setCustomizations({
      color: GAME_CONFIGS[initialCategory as keyof typeof GAME_CONFIGS].colors[0],
      size: GAME_CONFIGS[initialCategory as keyof typeof GAME_CONFIGS].sizes[0],
      extras: []
    })
  }, [initialCategory])

  const handleDragEnd = (e: any) => {
    const node = e.target
    const newCustomizations = { ...customizations }
    // Actualizar posición del elemento arrastrado
    setCustomizations(newCustomizations)
  }

  const handleColorChange = (color: string) => {
    setCustomizations(prev => ({ ...prev, color }))
  }

  const handleSizeChange = (size: string) => {
    setCustomizations(prev => ({ ...prev, size }))
  }

  const handleExtraAdd = (extra: string) => {
    setCustomizations(prev => ({
      ...prev,
      extras: prev.extras.includes(extra)
        ? prev.extras.filter(e => e !== extra)
        : [...prev.extras, extra]
    }))
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-center">
        <Stage
          width={400}
          height={500}
          ref={stageRef}
          className="border border-gray-200 rounded-lg bg-white"
        >
          <Layer>
            {/* Base del producto */}
            <Image
              image={baseImage}
              x={100}
              y={200}
              width={200}
              height={250}
              fill={customizations.color}
            />
            
            {/* Elemento secundario */}
            <Image
              image={lidImage}
              x={120}
              y={180}
              width={160}
              height={40}
              draggable
              onDragEnd={handleDragEnd}
            />
            
            {/* Accesorios */}
            <Image
              image={strawImage}
              x={250}
              y={150}
              width={20}
              height={100}
              draggable
              onDragEnd={handleDragEnd}
            />
          </Layer>
        </Stage>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="font-medium mb-2">Color</h4>
          <div className="flex gap-2">
            {config.colors.map((color) => (
              <button
                key={color}
                className="w-8 h-8 rounded-full border-2 border-gray-200 hover:scale-110 transition-transform"
                style={{ backgroundColor: color }}
                onClick={() => handleColorChange(color)}
              />
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-medium mb-2">Tamaño</h4>
          <div className="flex gap-2">
            {config.sizes.map((size) => (
              <button
                key={size}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  customizations.size === size
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-gray-200 hover:border-blue-200"
                }`}
                onClick={() => handleSizeChange(size)}
              >
                {size.charAt(0).toUpperCase() + size.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-medium mb-2">Extras</h4>
          <div className="flex flex-wrap gap-2">
            {config.extras.map((extra) => (
              <button
                key={extra}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  customizations.extras.includes(extra)
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-gray-200 hover:border-blue-200"
                }`}
                onClick={() => handleExtraAdd(extra)}
              >
                {extra}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
} 