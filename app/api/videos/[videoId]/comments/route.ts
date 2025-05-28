import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { redis } from "@/lib/redis";

export async function GET(req: NextRequest, { params }: { params: { videoId: string } }) {
  const { videoId } = params;
  const cacheKey = `video:${videoId}:comments`;
  // Try Redis first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return NextResponse.json(JSON.parse(cached));
  }
  // If not cached, fetch from DB
  const comments = await prisma.videoComment.findMany({
    where: { videoId },
    orderBy: { createdAt: "desc" },
    include: { user: true },
  });
  const result = comments.map((comment) => ({
    id: comment.id,
    content: comment.content,
    createdAt: comment.createdAt,
    user: {
      name: comment.user?.name,
      image: comment.user?.image,
    },
  }));
  // Cache in Redis for 60 seconds
  await redis.set(cacheKey, JSON.stringify(result), "EX", 60);
  return NextResponse.json(result);
}

export async function POST(
  request: Request,
  { params }: { params: { videoId: string } }
) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return new NextResponse("Unauthorized", { status: 401 });
    }

    const { content, image } = await request.json();
    if (!content) {
      return new NextResponse("Content is required", { status: 400 });
    }

    // Create comment object
    const comment = {
      id: Math.random().toString(36).substr(2, 9),
      content,
      createdAt: new Date().toISOString(),
      user: {
        name: session.user.name || "Usuario",
        image: image || session.user.image,
      },
    };

    return NextResponse.json(comment);
  } catch (error) {
    console.error("[VIDEO_COMMENTS_POST]", error);
    return new NextResponse("Internal Error", { status: 500 });
  }
} 