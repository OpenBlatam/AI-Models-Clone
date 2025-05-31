import { Academy } from "@/lib/types/academy";
import { blatamcursosAcademy } from "./academy-blatamcursos";
import { blatamcursosAcademy2 } from "./academy-blatamcursos-2";
import { fundamentosChatGPTAcademy } from "./academy-fundamentos-chatgpt";
import { imagenesChatGPTAcademy } from "./academy-imagenes-chatgpt";
import { videoChatGPTAcademy } from "./academy-video-chatgpt";
import { avanzadoChatGPTAcademy } from "./academy-avanzado-chatgpt";
import { programacionChatGPTAcademy } from "./academy-programacion-chatgpt";

export const academies: Academy[] = [
  fundamentosChatGPTAcademy,
  imagenesChatGPTAcademy,
  videoChatGPTAcademy,
  avanzadoChatGPTAcademy,
  programacionChatGPTAcademy,
  blatamcursosAcademy,
  blatamcursosAcademy2
];

export { fundamentosChatGPTAcademy } from "./academy-fundamentos-chatgpt";
export { imagenesChatGPTAcademy } from "./academy-imagenes-chatgpt";
export { videoChatGPTAcademy } from "./academy-video-chatgpt";
export { avanzadoChatGPTAcademy } from "./academy-avanzado-chatgpt";
export { programacionChatGPTAcademy } from "./academy-programacion-chatgpt"; 