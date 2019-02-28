export const API_ROOT = "https://pkapi.astrid.fun";

export type System = {
    members: Member[]
};

export type Member = {
    name: string,
    description: string
};