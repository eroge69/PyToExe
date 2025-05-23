stuff_to_check = "aeiyou"

took = input("Zadejte text na zkontrolování:\n").lower()

if set(stuff_to_check) & set(took):
    print("--\nAno, samohlásky zde existují:")
    for i in stuff_to_check:
        print(f"{i}: {took.count(i)}")
else:
    print("--\nŽÁDNÉ SAMOHLÁSKY!")
input()
