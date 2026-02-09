// Common Utility Types

export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type Maybe<T> = T | null | undefined;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

export type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

export type KeysOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

export type ValuesOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? T[K] : never;
}[keyof T];

export type OptionalKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? K : never;
}[keyof T];

export type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K;
}[keyof T];

export type FunctionPropertyNames<T> = {
  [K in keyof T]: T[K] extends Function ? K : never;
}[keyof T];

export type NonFunctionPropertyNames<T> = {
  [K in keyof T]: T[K] extends Function ? never : K;
}[keyof T];

export type PromiseReturnType<T> = T extends Promise<infer U> ? U : T;

export type AsyncFunction<T extends (...args: any[]) => any> = (
  ...args: Parameters<T>
) => Promise<ReturnType<T>>;

export type ExtractProps<T> = T extends React.ComponentType<infer P> ? P : never;

export type ComponentProps<T extends keyof JSX.IntrinsicElements | React.JSXElementConstructor<any>> =
  React.ComponentProps<T>;

export type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

export type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};

export type Record<K extends keyof any, T> = {
  [P in K]: T;
};

export type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

export type Partial<T> = {
  [P in keyof T]?: T[P];
};

export type Required<T> = {
  [P in keyof T]-?: T[P];
};

export type NonNullable<T> = T extends null | undefined ? never : T;

export type Awaited<T> = T extends Promise<infer U> ? U : T;

export type ArrayElement<ArrayType extends readonly unknown[]> = ArrayType extends readonly (infer ElementType)[]
  ? ElementType
  : never;

export type TupleToUnion<T extends readonly unknown[]> = T[number];

export type UnionToIntersection<U> = (U extends any ? (k: U) => void : never) extends (k: infer I) => void
  ? I
  : never;

export type StringKeys<T> = Extract<keyof T, string>;

export type NumberKeys<T> = Extract<keyof T, number>;

export type SymbolKeys<T> = Extract<keyof T, symbol>;

export type Brand<T, B> = T & { __brand: B };

export type Nominal<T, B> = T & { readonly __nominal: B };

export type Timestamp = Brand<number, 'Timestamp'>;

export type ID = Brand<string, 'ID'>;

export type Email = Brand<string, 'Email'>;

export type URL = Brand<string, 'URL'>;

export type Currency = Brand<string, 'Currency'>;

export type Percentage = Brand<number, 'Percentage'>;

export type PositiveNumber = Brand<number, 'PositiveNumber'>;

export type NonNegativeNumber = Brand<number, 'NonNegativeNumber'>;

export type Integer = Brand<number, 'Integer'>;

export type NonEmptyString = Brand<string, 'NonEmptyString'>;

