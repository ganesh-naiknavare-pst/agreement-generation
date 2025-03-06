import { useEffect } from "react";
import useApi, { BackendEndpoints } from "./useApi";

export interface Agreement {
  id: number;
  address: string;
  city: string;
  startDate: string;
  pdf: string;
  owner: {
    name: string;
    email: string;
  }[];
  tenants: {
    name: string;
    email: string;
  }[];
  status: string;
}

export interface TemplateAgreement {
  id: number;
  address: string;
  city: string;
  createdAt: string;
  pdf: string;
  authority: {
    email: string;
  }[];
  participant: {
    email: string;
  }[];
  status: string;
}

export const useAgreements = () => {
  const {
    data: rentAgreement,
    loading: loadRentAgreemnts,
    error: rentAgreementError,
    fetchData: fetchAgreements,
  } = useApi<Agreement[]>(BackendEndpoints.GetAgreements);
  const {
    data: templateAgreement,
    loading: loadTemplatetAgreemnts,
    error: templateAgreementError,
    fetchData: fetchTemplateAgreements,
  } = useApi<TemplateAgreement[]>(BackendEndpoints.GetTemplateAgreements);

  useEffect(() => {
    fetchAgreements({ method: "GET" });
    fetchTemplateAgreements({ method: "GET" });
  }, []);

  return {
    agreements: rentAgreement,
    loadRentAgreemnts,
    rentAgreementError,
    fetchAgreements,
    templateAgreement,
    loadTemplatetAgreemnts,
    templateAgreementError,
    fetchTemplateAgreements,
  };
};
