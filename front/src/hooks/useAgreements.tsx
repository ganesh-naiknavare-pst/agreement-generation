import { createContext, useContext, ReactNode, useEffect } from "react";
import useApi, { BackendEndpoints } from "./useApi";
import { useUser } from "@clerk/clerk-react";
import { Agreement, TemplateAgreement } from "../types/types";

interface AgreementContextType {
  agreements: Agreement[] | null;
  loadRentAgreemnts: boolean;
  fetchAgreements: (method: {}) => Promise<void>;
  templateAgreement: TemplateAgreement[] | null;
  loadTemplatetAgreemnts: boolean;
  fetchTemplateAgreements: (method: {}) => Promise<void>;
}

const AgreementsContext = createContext<AgreementContextType>({
  agreements: [],
  loadRentAgreemnts: false,
  fetchAgreements: (method: {}) => Promise.resolve(),
  templateAgreement: [],
  loadTemplatetAgreemnts: false,
  fetchTemplateAgreements: (method: {}) => Promise.resolve(),
});

export const AgreementsProvider = ({ children }: { children: ReactNode }) => {
  const { user } = useUser();
  const {
    data: agreements,
    loading: loadRentAgreemnts,
    fetchData: fetchAgreements,
  } = useApi<Agreement[]>(BackendEndpoints.GetAgreements);
  const {
    data: templateAgreement,
    loading: loadTemplatetAgreemnts,
    fetchData: fetchTemplateAgreements,
  } = useApi<TemplateAgreement[]>(BackendEndpoints.GetTemplateAgreements);

  useEffect(() => {
    fetchAgreements({ method: "GET", params: { user_id: user?.id } });
    fetchTemplateAgreements({ method: "GET", params: { user_id: user?.id } });
  }, []);

  return (
    <AgreementsContext.Provider
      value={{
        agreements,
        loadRentAgreemnts,
        fetchAgreements,
        templateAgreement,
        loadTemplatetAgreemnts,
        fetchTemplateAgreements,
      }}
    >
      {children}
    </AgreementsContext.Provider>
  );
};

export const useAgreements = () => useContext(AgreementsContext);
