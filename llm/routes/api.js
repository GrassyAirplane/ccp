import express from "express";

const APIRouter = express.Router();
const router = APIRouter;

router.post("/ask", ask);

export default APIRouter;
