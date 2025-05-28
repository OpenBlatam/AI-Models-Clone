import { useState } from "react";
import { VideoPlayer } from "@/components/videos/VideoPlayer";
import { VideoHeader } from "@/components/videos/VideoHeader";
import { VideoResumen } from "@/components/videos/VideoResumen";
import { VideoResources } from "@/components/videos/VideoResources";
import { VideoComments } from "@/components/videos/VideoComments";
import { VideoQuestionBar } from "@/components/videos/VideoQuestionBar";
import { VideoSidebar } from "@/components/videos/VideoSidebar";
import { Button } from "@/components/ui/button";
import { Video } from "lucide-react";

// Apollo Client for AppSync
import { ApolloClient, InMemoryCache, ApolloProvider, useSubscription, useMutation, gql, split, HttpLink } from "@apollo/client";
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';
import { getMainDefinition } from '@apollo/client/utilities';

// TODO: Replace with your real AppSync GraphQL endpoint and authentication
const APPSYNC_URL = "wss://your-appsync-endpoint.appsync-api.us-east-1.amazonaws.com/graphql";
const APPSYNC_HTTP_URL = "https://your-appsync-endpoint.appsync-api.us-east-1.amazonaws.com/graphql";

const wsLink = new GraphQLWsLink(createClient({
  url: APPSYNC_URL,
  // TODO: Add authentication headers if needed
}));
const httpLink = new HttpLink({ uri: APPSYNC_HTTP_URL });
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink
);
const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});

const ON_NEW_COMMENT = gql`
  subscription OnNewComment($videoId: ID!) {
    onNewComment(videoId: $videoId) {
      id
      content
      createdAt
      user {
        name
        image
      }
    }
  }
`;

const ADD_COMMENT = gql`
  mutation AddComment($videoId: ID!, $content: String!) {
    addComment(videoId: $videoId, content: $content) {
      id
      content
      createdAt
      user {
        name
        image
      }
    }
  }
`;

// TODO: Replace with real data from DynamoDB or AppSync
const mockVideos = [
  {
    id: "1",
    title: "Video AWS S3 + CloudFront",
    description: "Video servido desde AWS S3 y CloudFront",
    url: "https://your-cloudfront-domain/videos/video1.m3u8",
    duration: "15:30",
    resumen: "# Video en AWS\n\nEste video es servido desde AWS S3 y CloudFront...",
    files: [],
    readings: [],
    comments: [],
  },
];

function ScalableVideosPageInner() {
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [currentTab, setCurrentTab] = useState("resumen");
  const currentVideo = mockVideos[currentVideoIndex];

  // Real-time comments with AppSync subscription
  const { data: subData } = useSubscription(ON_NEW_COMMENT, {
    variables: { videoId: currentVideo.id },
  });
  const comments = subData?.onNewComment ? [subData.onNewComment] : [];

  // Add comment mutation
  const [addComment] = useMutation(ADD_COMMENT);
  const handleAddComment = async (content: string) => {
    await addComment({ variables: { videoId: currentVideo.id, content } });
  };

  return (
    <div className="flex min-h-screen bg-zinc-950 text-white">
      <VideoSidebar
        videos={mockVideos}
        currentVideoId={currentVideo.id}
        onSelectVideo={(id) => {
          const idx = mockVideos.findIndex((v) => v.id === id);
          if (idx !== -1) setCurrentVideoIndex(idx);
        }}
      />
      <main className="flex-1 flex flex-col items-center p-4 md:p-8">
        <div className="w-full max-w-7xl">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold">Videos (Escalable AWS)</h1>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Video className="w-4 h-4 mr-2" />
              Subir video
            </Button>
          </div>
          <section className="bg-zinc-900 rounded-2xl shadow-lg p-0 md:p-8 flex flex-col gap-6 w-full max-w-5xl mx-auto mb-8">
            <VideoHeader
              video={currentVideo}
              currentTab={currentTab}
              onTabChange={setCurrentTab}
            />
            <VideoPlayer
              src={currentVideo.url}
              onTimeUpdate={(time) => {}}
              onEnded={() => {}}
            />
            {currentTab === "resumen" && <VideoResumen resumen={currentVideo.resumen} />}
            {currentTab === "recursos" && <VideoResources files={currentVideo.files} readings={currentVideo.readings} />}
            {currentTab === "comentarios" && (
              <VideoComments comments={comments} onAddComment={handleAddComment} />
            )}
            <VideoQuestionBar onAsk={handleAddComment} />
          </section>
        </div>
      </main>
    </div>
  );
}

export default function ScalableVideosPage() {
  return (
    <ApolloProvider client={client}>
      <ScalableVideosPageInner />
    </ApolloProvider>
  );
} 