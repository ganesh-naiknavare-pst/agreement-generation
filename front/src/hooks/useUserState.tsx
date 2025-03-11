import { createContext, useContext, ReactNode, useEffect } from "react";
import useApi, { BackendEndpoints } from "./useApi";
import { useParams, useSearchParams } from "react-router-dom";
export type UserData = {
  id: number;
  userId: string;
  agreementId: number;
  status: string;
};

interface UserContextType {
  rentAgreementUser: UserData | null;
  getRentAgreementUser: (method: {}) => Promise<void>;
  TemplateAgreementUser: UserData | null;
  getTemplateAgreementUser: (method: {}) => Promise<void>;
}

const UserContext = createContext<UserContextType>({
  rentAgreementUser: {
    id: 0,
    userId: "",
    agreementId: 0,
    status: "PROCESSING",
  },
  getRentAgreementUser: () => Promise.resolve(),
  TemplateAgreementUser: {
    id: 0,
    userId: "",
    agreementId: 0,
    status: "PROCESSING",
  },
  getTemplateAgreementUser: () => Promise.resolve(),
});

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const { data: rentAgreementUser, fetchData: getRentAgreementUser } =
    useApi<UserData>(BackendEndpoints.GetRentAgreementUser);
  const { data: TemplateAgreementUser, fetchData: getTemplateAgreementUser } =
    useApi<UserData>(BackendEndpoints.GetTemplateAgreementUSer);
  const param = useParams();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    if (param.id && param.agreementId) {
      const requestData = {
        agreement_id: param.agreementId,
        user_id: param.id,
      };
      if (searchParams.get("type") === "rent") {
        getRentAgreementUser({ method: "GET", params: requestData });
      } else {
        getTemplateAgreementUser({ method: "GET", params: requestData });
      }
    }
  }, []);

  return (
    <UserContext.Provider
      value={{
        rentAgreementUser,
        getRentAgreementUser,
        TemplateAgreementUser,
        getTemplateAgreementUser,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useUserState = () => useContext(UserContext);
