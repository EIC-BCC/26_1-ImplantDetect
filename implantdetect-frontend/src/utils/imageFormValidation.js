import * as yup from 'yup';

const validFileExtensions = ['jpg', 'jpeg', 'png'];

const validFileSize = 1024 * 1024 * 15;

function isValidFileType(fileName) {
    return fileName && validFileExtensions.includes(fileName.split('.').pop().toLowerCase());
}

export const imageFormSchema = yup.object().shape({
    file: yup.mixed()
        .required('Arquivo é obrigatório.')
        .test("is-valid-size", "Arquivo é maior que 15MB.", value => {
            return value && value.size <= validFileSize;
        })
        .test("is-valid-type", "Tipo de arquivo não suportado.", value => {
            return value && isValidFileType(value.name);
        }),
});
