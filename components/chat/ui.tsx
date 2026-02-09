// This file has been refactored. See ChatPageRefactored.tsx for the new implementation.
// This file is kept for backward compatibility but will be deprecated.

export { default } from "./ChatPageRefactored";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: crypto.randomUUID(),
      type: "bot",
      text: "Hola 👋, escribe `imagen un dragón volando` o hazme una pregunta.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [agents, setAgents] = useState<Agent[]>([]);
  // const toast = useToast(); // Removed due to compatibility issues
  const scrollRef = useRef<HTMLDivElement>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = useRef<HTMLButtonElement>(null);
  const [agentToDelete, setAgentToDelete] = useState<string | null>(null);

  // Load agents from localStorage on mount
  useEffect(() => {
    try {
      const storedAgents = localStorage.getItem(AGENTS_STORAGE_KEY);
      if (storedAgents) {
        setAgents(JSON.parse(storedAgents));
      }
    } catch (error) {
      console.error("Error loading agents:", error);
    }
  }, []);

  // Save agents to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(AGENTS_STORAGE_KEY, JSON.stringify(agents));
    } catch (error) {
      console.error("Error saving agents:", error);
    }
  }, [agents]);

  const handleDeleteAgent = (agentId: string) => {
    setAgentToDelete(agentId);
    onOpen();
  };

  const confirmDeleteAgent = () => {
    if (agentToDelete) {
      setAgents((prev) => prev.filter((agent) => agent.id !== agentToDelete));
      setAgentToDelete(null);
      onClose();
    }
  };

  const handleDeleteAllAgents = () => {
    setAgents([]);
    onClose();
  };

  // Auto scroll to bottom
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 150;
    if (isNearBottom) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  const addMessage = useCallback(
    (msg: Omit<Message, "id">) => {
      setMessages((prev) => [...prev, { ...msg, id: crypto.randomUUID() }]);
    },
    [setMessages]
  );

  // Handle sending text or image generation
  const handleSend = async () => {
    if (!input.trim()) return;
    addMessage({ type: "user", text: input });
    setLoading(true);
    setIsTyping(true);
    const prompt = input.trim();
    setInput("");

    try {
      if (prompt.toLowerCase().startsWith("imagen ")) {
        const imagePrompt = prompt.slice(7);

        const response = await fetch("https://openrouter.ai/api/v1/generate", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${OPENROUTER_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: "openai/dall-e-3",
            prompt: imagePrompt,
            size: "1024x1024",
          }),
        });

        const data = await response.json();
        if (data?.url) {
          addMessage({ type: "bot", image: data.url });
        } else {
          console.error("No se pudo generar la imagen.");
          addMessage({ type: "bot", text: "❌ No se pudo generar la imagen." });
        }
      } else {
        // Chat completion call (api/chat)
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt }),
        });
        const data = await response.json();

        if (data?.text) {
          addMessage({ type: "bot", text: data.text });
        } else {
          console.error("No se pudo obtener respuesta del modelo.");
          addMessage({ type: "bot", text: "❌ No se pudo obtener respuesta." });
        }
      }
    } catch (error) {
      console.error("Ocurrió un error inesperado.");
      addMessage({ type: "bot", text: "❌ Error en la petición." });
    } finally {
      setLoading(false);
      setIsTyping(false);
    }
  };

  // Drag and drop usando react-dropzone
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      acceptedFiles.forEach(async (file) => {
        if (!file.type.startsWith("image/")) return;
        setLoading(true);
        setIsTyping(true);
        addMessage({ type: "user", image: URL.createObjectURL(file) });

        // Aquí se puede enviar el archivo a backend o API de generación para reconocimiento o almacenamiento
        // Simulación de respuesta rápida de bot
        setTimeout(() => {
          addMessage({ type: "bot", text: "Imagen recibida correctamente 📷" });
          setLoading(false);
          setIsTyping(false);
        }, 1200);
      });
    },
    [addMessage]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { "image/*": [] } });

  return (
    <Flex
      direction="column"
      height="100vh"
      bgGradient="linear(to-br, gray.900, gray.800)"
      color="white"
      p={4}
      maxW="3xl"
      mx="auto"
      borderRadius="xl"
      boxShadow="2xl"
    >
      <chakra.header
        fontWeight="bold"
        fontSize="xl"
        textAlign="center"
        p={3}
        borderBottom="1px solid"
        borderColor="gray.700"
        userSelect="none"
        position="relative"
      >
        ChatGPT - UI Mejorada con Chakra UI
        {agents.length > 0 && (
          <Box position="absolute" right={2} top="50%" transform="translateY(-50%)">
            <Menu>
              <MenuButton
                as={IconButton}
                icon={<MoreVerticalIcon size={18} />}
                aria-label="Opciones de agentes"
                variant="ghost"
                colorScheme="gray"
                size="sm"
              />
              <MenuList bg="gray.800" borderColor="gray.700">
                <MenuItem
                  bg="gray.800"
                  _hover={{ bg: "gray.700" }}
                  onClick={() => {
                    setAgentToDelete("all");
                    onOpen();
                  }}
                  icon={<Trash2Icon size={16} />}
                >
                  Borrar todos los agentes
                </MenuItem>
              </MenuList>
            </Menu>
          </Box>
        )}
      </chakra.header>

      <Box
        flex="1"
        overflowY="auto"
        mt={4}
        mb={4}
        px={2}
        {...getRootProps()}
        borderWidth="2px"
        borderColor={isDragActive ? "blue.400" : "gray.700"}
        borderStyle="dashed"
        borderRadius="md"
        position="relative"
        _focusWithin={{ boxShadow: "outline" }}
        aria-label="Área de mensajes y arrastrar imagenes"
      >
        <input {...getInputProps()} aria-label="Subir imagenes" />

        {isDragActive && (
          <Box
            position="absolute"
            inset={0}
            bg="blue.500"
            opacity={0.25}
            borderRadius="md"
            zIndex={10}
            pointerEvents="none"
            display="flex"
            alignItems="center"
            justifyContent="center"
            fontWeight="bold"
            fontSize="lg"
            color="white"
          >
            Suelta para subir imágenes
          </Box>
        )}

        <AnimatePresence initial={false}>
          {messages.map(({ id, type, text, image }) => {
            const isUser = type === "user";
            return (
              <MotionBox
                key={id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 15 }}
                mb={4}
                display="flex"
                justifyContent={isUser ? "flex-end" : "flex-start"}
              >
                <Box
                  maxW="70%"
                  bg={isUser ? "blue.600" : "gray.700"}
                  color="white"
                  p={4}
                  borderRadius="2xl"
                  position="relative"
                  _after={{
                    content: '""',
                    position: "absolute",
                    bottom: 0,
                    width: 8,
                    height: 8,
                    backgroundColor: isUser ? "blue.600" : "gray.700",
                    transform: isUser ? "translateX(50%) rotate(45deg)" : "translateX(-50%) rotate(45deg)",
                    left: isUser ? "100%" : "0",
                    borderBottomRightRadius: 2,
                  }}
                >
                  {image ? (
                    <img
                      src={image}
                      alt="Imagen generada"
                      style={{
                        borderRadius: "8px",
                        maxWidth: "100%",
                        maxHeight: "400px",
                        objectFit: "contain"
                      }}
                      loading="lazy"
                    />
                  ) : (
                    <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap">
                      <ReactMarkdown
                        components={{
                          p: (props) => <Text mb={2} {...props} />,
                          a: (props) => (
                            <a
                              {...props}
                              style={{
                                color: "#63b3ed",
                                textDecoration: "underline"
                              }}
                              target="_blank"
                              rel="noopener noreferrer"
                            />
                          ),
                        }}
                      >
                        {text || ""}
                      </ReactMarkdown>
                    </div>
                  )}
                </Box>
              </MotionBox>
            );
          })}
        </AnimatePresence>

        {isTyping && (
          <Flex align="center" color="gray.400" mb={2} pl={2}>
            <Spinner size="sm" mr={2} />
            Escribiendo...
          </Flex>
        )}

        <div ref={scrollRef} />
      </Box>

      {/* Agent List Section */}
      {agents.length > 0 && (
        <Box
          mb={4}
          p={3}
          bg="gray.800"
          borderRadius="md"
          borderWidth="1px"
          borderColor="gray.700"
        >
          <Text fontSize="sm" fontWeight="semibold" mb={2} color="gray.300">
            Agentes ({agents.length})
          </Text>
          <Flex direction="column" gap={2} maxH="150px" overflowY="auto">
            {agents.map((agent) => (
              <Flex
                key={agent.id}
                justify="space-between"
                align="center"
                p={2}
                bg="gray.700"
                borderRadius="md"
                _hover={{ bg: "gray.600" }}
              >
                <Text fontSize="sm" color="white" flex="1">
                  {agent.name}
                </Text>
                <IconButton
                  icon={<Trash2Icon size={16} />}
                  aria-label={`Borrar agente ${agent.name}`}
                  size="sm"
                  colorScheme="red"
                  variant="ghost"
                  onClick={() => handleDeleteAgent(agent.id)}
                />
              </Flex>
            ))}
          </Flex>
        </Box>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent bg="gray.800" color="white">
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              {agentToDelete === "all" ? "Borrar todos los agentes" : "Borrar agente"}
            </AlertDialogHeader>
            <AlertDialogBody>
              {agentToDelete === "all"
                ? "¿Estás seguro de que quieres borrar todos los agentes? Esta acción no se puede deshacer."
                : "¿Estás seguro de que quieres borrar este agente? Esta acción no se puede deshacer."}
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose} colorScheme="gray">
                Cancelar
              </Button>
              <Button
                colorScheme="red"
                onClick={agentToDelete === "all" ? handleDeleteAllAgents : confirmDeleteAgent}
                ml={3}
              >
                Borrar
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!loading) handleSend();
        }}
      >
        <Flex gap={2} align="end">
          <Textarea
            resize="vertical"
            rows={1}
            maxHeight="150px"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe 'imagen un dragón' o hazme una pregunta..."
            disabled={loading}
            aria-label="Entrada de texto"
            flex="1"
          />
          <Button
            colorScheme="blue"
            type="submit"
            loading={loading}
            loadingText="Enviando"
            aria-label="Enviar mensaje"
          >
            Enviar <ArrowUpIcon style={{ marginLeft: '8px', width: '16px', height: '16px' }} />
          </Button>
        </Flex>
      </form>
    </Flex>
  );
}
