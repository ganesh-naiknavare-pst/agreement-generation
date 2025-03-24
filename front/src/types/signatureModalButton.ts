import CanvasDraw from "react-canvas-draw";

export interface CanvasDrawProps {
  loadTimeOffset: number;
  lazyRadius: number;
  brushRadius: number;
  catenaryColor: string;
  gridColor: string;
  hideGrid: boolean;
  canvasWidth: number;
  canvasHeight: number;
  disabled: boolean;
  imgSrc: string;
  saveData: string;
  immediateLoading: boolean;
  hideInterface: boolean;
  brushColor?: string;
  className?: string;
  onChange?: () => void;
}

export interface CanvasDrawExtended extends CanvasDraw {
  canvasContainer: {
    children: HTMLCanvasElement[];
  };
}

export const defaultProps: CanvasDrawProps = {
  loadTimeOffset: 5,
  lazyRadius: 0,
  brushRadius: 3,
  catenaryColor: "#1976d2",
  gridColor: "rgba(200,200,200,0.2)",
  hideGrid: false,
  canvasWidth: 500,
  canvasHeight: 200,
  disabled: false,
  imgSrc: "",
  saveData: "",
  immediateLoading: false,
  hideInterface: false,
};

export interface SignatureModalProps {
  onSignatureSave: (signatureData: string) => void;
}
