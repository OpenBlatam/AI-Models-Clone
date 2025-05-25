import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/auth";
import prisma from "@/lib/prisma";

// GET /api/notes/[id] - Obtener un apunte específico
export async function GET(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.id) {
      return new NextResponse("No autorizado", { status: 401 });
    }

    const note = await prisma.note.findUnique({
      where: {
        id: params.id,
        userId: session.user.id,
      },
    });

    if (!note) {
      return new NextResponse("Apunte no encontrado", { status: 404 });
    }

    return NextResponse.json(note);
  } catch (error) {
    console.error("[NOTE_GET]", error);
    return new NextResponse("Error interno", { status: 500 });
  }
}

// PUT /api/notes/[id] - Actualizar un apunte
export async function PUT(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.id) {
      return new NextResponse("No autorizado", { status: 401 });
    }

    const body = await req.json();
    const { title, content } = body;

    if (!title || !content) {
      return new NextResponse("Faltan campos requeridos", { status: 400 });
    }

    const note = await prisma.note.update({
      where: {
        id: params.id,
        userId: session.user.id,
      },
      data: {
        title,
        content,
      },
    });

    return NextResponse.json(note);
  } catch (error) {
    console.error("[NOTE_PUT]", error);
    return new NextResponse("Error interno", { status: 500 });
  }
}

// DELETE /api/notes/[id] - Eliminar un apunte
export async function DELETE(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.id) {
      return new NextResponse("No autorizado", { status: 401 });
    }

    await prisma.note.delete({
      where: {
        id: params.id,
        userId: session.user.id,
      },
    });

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error("[NOTE_DELETE]", error);
    return new NextResponse("Error interno", { status: 500 });
  }
} 